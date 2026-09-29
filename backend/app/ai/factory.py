import logging
from typing import List, Optional, Dict, Any, Callable, TypeVar
from pydantic import BaseModel

from ..config import settings
from .base import AIProvider
from .schemas import RoadmapData, AnalysisResult, AdjustmentSuggestion, MonthlySummary
from .exceptions import (
    AIServiceException,
    AIProviderError,
    AIAuthenticationError,
    AIRateLimitError,
    AITimeoutError,
    AIConnectionError,
    AIResponseValidationError,
    AIConfigurationError,
)
from .openai_service import OpenAIService
from .gemini_service import GeminiService
from .groq_service import GroqService
from .mock_ai_service import MockAIService

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Transient provider-level exceptions eligible for automated fallback
TRANSIENT_FALLBACK_EXCEPTIONS = (
    AIRateLimitError,
    AITimeoutError,
    AIConnectionError,
    AIAuthenticationError,
    AIConfigurationError,
    AIProviderError,
)


class FallbackChainService(AIProvider):
    """
    Orchestrates an AI provider fallback chain.
    Attempts primary provider first; if transient provider availability fails (quota, timeout, 5xx),
    attempts configured fallbacks in sequential order at most once per request.
    Strictly avoids retries on application, authorization, or schema validation failures.
    """

    def __init__(self, providers: List[AIProvider]):
        if not providers:
            raise ValueError("FallbackChainService requires at least one AI provider.")
        self.providers = providers
        self.primary = providers[0]
        self.provider_name = f"chain({','.join(p.provider_name for p in providers)})"
        self.model = self.primary.model

    def _execute_with_fallback(self, operation_name: str, op_callable: Callable[[AIProvider], T]) -> T:
        last_exception = None

        for index, provider in enumerate(self.providers):
            try:
                logger.info(
                    f"AI request provider={provider.provider_name} model={provider.model} operation={operation_name}"
                )
                result = op_callable(provider)
                return result
            except TRANSIENT_FALLBACK_EXCEPTIONS as err:
                last_exception = err
                is_last_provider = (index == len(self.providers) - 1)
                
                # Check HTTP status codes: 429, 502, 503, 504 are transient
                status = getattr(err, "status_code", 502)
                if status not in (429, 502, 503, 504):
                    # Not a transient infrastructure error; immediately raise
                    raise

                if is_last_provider:
                    logger.error(
                        f"All AI providers in fallback chain exhausted for operation={operation_name}. "
                        f"Final failure on provider={provider.provider_name}: {err.detail if hasattr(err, 'detail') else str(err)}"
                    )
                    raise
                else:
                    next_provider = self.providers[index + 1]
                    logger.warning(
                        f"AI provider failed provider={provider.provider_name} error_type={type(err).__name__}. "
                        f"Triggering fallback provider={next_provider.provider_name} for operation={operation_name}"
                    )
            except AIResponseValidationError:
                # Do not fallback on schema validation or malformed application data
                logger.error(f"AI response validation error on provider={provider.provider_name}; aborting fallback chain.")
                raise
            except Exception as e:
                # Unexpected application or programming error; do not mask with fallback
                logger.error(f"Unexpected non-transient error in AI provider={provider.provider_name}: {e}")
                raise

        if last_exception:
            raise last_exception
        raise AIProviderError("No AI provider was able to fulfill the request.")

    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        return self._execute_with_fallback("generate_roadmap", lambda p: p.generate_roadmap(goal_info))

    def analyze_week(
        self,
        checkin_data: Dict[str, Any],
        goal_info: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> AnalysisResult:
        return self._execute_with_fallback(
            "analyze_week",
            lambda p: p.analyze_week(checkin_data, goal_info, progress)
        )

    def suggest_adjustment(
        self,
        analysis: Dict[str, Any],
        roadmap: Dict[str, Any],
        remaining_weeks: int
    ) -> AdjustmentSuggestion:
        return self._execute_with_fallback(
            "suggest_adjustment",
            lambda p: p.suggest_adjustment(analysis, roadmap, remaining_weeks)
        )

    def generate_monthly_summary(
        self,
        goal: Dict[str, Any],
        checkins: List[Dict[str, Any]],
        progress_records: List[Dict[str, Any]]
    ) -> MonthlySummary:
        return self._execute_with_fallback(
            "generate_monthly_summary",
            lambda p: p.generate_monthly_summary(goal, checkins, progress_records)
        )


def create_provider_instance(name: str) -> AIProvider:
    """Instantiates a provider by name."""
    clean_name = (name or "").strip().lower()
    if clean_name == "openai":
        return OpenAIService()
    elif clean_name == "gemini":
        return GeminiService()
    elif clean_name == "groq":
        return GroqService()
    elif clean_name == "mock":
        return MockAIService()
    else:
        raise AIConfigurationError(f"Unsupported AI provider: '{name}'. Supported: 'openai', 'gemini', 'groq', 'mock'")


create_provider = create_provider_instance


def get_ai_service(provider: Optional[str] = None) -> AIProvider:
    """
    Factory function returning the active AI provider or FallbackChainService.
    If provider is explicitly provided, returns that specific single provider.
    Otherwise builds from settings.AI_PROVIDER and settings.fallback_provider_list.
    """
    if provider:
        return create_provider_instance(provider)

    primary_name = (getattr(settings, "AI_PROVIDER", "openai") or "openai").strip().lower()
    fallback_names = getattr(settings, "fallback_provider_list", [])

    if not fallback_names:
        return create_provider_instance(primary_name)

    # Build fallback chain
    providers = [create_provider_instance(primary_name)]
    for fb_name in fallback_names:
        providers.append(create_provider_instance(fb_name))

    return FallbackChainService(providers)
