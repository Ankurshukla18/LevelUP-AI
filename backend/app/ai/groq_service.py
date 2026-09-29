import json
import logging
from typing import Dict, Any, Type, TypeVar, Optional, List
from pydantic import BaseModel, ValidationError

try:
    import groq
    from groq import Groq
except ImportError:
    groq = None
    Groq = None

from ..config import settings
from .base import AIProvider
from .schemas import (
    RoadmapData,
    AnalysisResult,
    AdjustmentSuggestion,
    MonthlySummary
)
from .prompts import (
    SYSTEM_INSTRUCTION,
    ROADMAP_INSTRUCTION,
    WEEKLY_ANALYSIS_INSTRUCTION,
    MONTHLY_SUMMARY_INSTRUCTION
)
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

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GroqService(AIProvider):
    """
    Groq AI Service implementing AIProvider via official groq Python SDK.
    Uses ultra-fast Llama models with JSON mode and validates strictly against Pydantic schemas.
    """

    provider_name: str = "groq"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else getattr(settings, "GROQ_API_KEY", None)
        self.model = model or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self._client = None

    @property
    def client(self):
        if not self.api_key:
            raise AIConfigurationError(
                detail="Groq API key is not configured. Please set GROQ_API_KEY in the backend environment."
            )
        if self._client is None:
            if Groq is None:
                raise AIConfigurationError(
                    detail="Groq library is not installed. Please install groq."
                )
            self._client = Groq(api_key=self.api_key)
        return self._client

    def _call_groq(self, instruction: str, user_data: Dict[str, Any], schema_cls: Type[T]) -> T:
        """
        Executes call to Groq with JSON object response mode and prompt injection protection.
        """
        user_content = json.dumps(user_data, default=str, indent=2)
        formatted_prompt = (
            f"<USER_DATA_START>\n"
            f"{user_content}\n"
            f"<USER_DATA_END>\n\n"
            f"Analyze the above user data and generate the required response strictly adhering to the schema."
        )

        full_system_instruction = f"{SYSTEM_INSTRUCTION}\n\n{instruction}"

        raw_output_text = None

        try:
            logger.info(f"AI request provider={self.provider_name} model={self.model} operation=call")

            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_instruction},
                    {"role": "user", "content": formatted_prompt}
                ],
                response_format={"type": "json_object"}
            )

            if chat_completion.choices and chat_completion.choices[0].message:
                raw_output_text = chat_completion.choices[0].message.content

        except Exception as err:
            err_str = str(err).lower()
            logger.error(f"AI provider failed provider={self.provider_name} error_type={type(err).__name__}")

            if groq is not None and isinstance(err, groq.AuthenticationError):
                raise AIAuthenticationError(
                    detail="Groq authentication failed. Invalid API key provided in server configuration."
                ) from err
            elif groq is not None and isinstance(err, groq.RateLimitError):
                raise AIRateLimitError(
                    detail="Groq rate limit or quota exceeded. Please check Groq account limits."
                ) from err
            elif groq is not None and isinstance(err, groq.APITimeoutError):
                raise AITimeoutError(
                    detail="Groq API request timed out. Please try again in a few moments."
                ) from err
            elif groq is not None and isinstance(err, groq.APIConnectionError):
                raise AIConnectionError(
                    detail="Unable to reach Groq API service. Please verify server internet connectivity."
                ) from err
            elif "rate" in err_str or "429" in err_str or "quota" in err_str:
                raise AIRateLimitError(
                    detail="Groq rate limit exceeded."
                ) from err
            elif "auth" in err_str or "401" in err_str or "api_key" in err_str:
                raise AIAuthenticationError(
                    detail="Groq authentication failed. Invalid API key."
                ) from err
            elif "timeout" in err_str or "504" in err_str:
                raise AITimeoutError(
                    detail="Groq API request timed out."
                ) from err
            elif "connection" in err_str or "503" in err_str:
                raise AIConnectionError(
                    detail="Unable to connect to Groq service."
                ) from err
            else:
                safe_detail = self.sanitize_error(str(err))
                raise AIProviderError(
                    detail=f"Groq API error: {safe_detail}"
                ) from err

        if not raw_output_text:
            raise AIResponseValidationError(
                detail="Groq returned an empty response."
            )

        # Strict Pydantic Schema Validation
        cleaned_text = self.clean_json_text(raw_output_text)
        try:
            parsed_data = json.loads(cleaned_text)
            validated_object = schema_cls.model_validate(parsed_data)
            return validated_object
        except (json.JSONDecodeError, ValidationError) as val_err:
            logger.error(f"Groq response validation failed: {val_err}. Raw output was: {raw_output_text[:300]}")
            raise AIResponseValidationError(
                detail="Groq returned a response that failed strict application schema validation."
            ) from val_err

    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        payload = {
            "title": goal_info.get("name") or goal_info.get("title", ""),
            "category": str(goal_info.get("category", "")),
            "description": goal_info.get("description", ""),
            "current_level": goal_info.get("current_level", "Beginner"),
            "target_outcome": goal_info.get("target_outcome", ""),
            "start_date": str(goal_info.get("start_date", "")),
            "target_date": str(goal_info.get("target_date", "")),
            "available_hours_per_week": goal_info.get("available_hours_per_week", 5.0),
            "priority": str(goal_info.get("priority", "medium")),
            "preferred_days": goal_info.get("preferred_days")
        }

        return self._call_groq(
            instruction=ROADMAP_INSTRUCTION,
            user_data=payload,
            schema_cls=RoadmapData
        )

    def analyze_week(
        self,
        checkin_data: Dict[str, Any],
        goal_info: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> AnalysisResult:
        payload = {
            "goal": {
                "title": goal_info.get("name") or goal_info.get("title", ""),
                "category": str(goal_info.get("category", "")),
                "target_outcome": goal_info.get("target_outcome", ""),
                "available_hours_per_week": goal_info.get("available_hours_per_week", 5.0),
            },
            "roadmap_week": {
                "week_number": checkin_data.get("week_number"),
                "week_title": checkin_data.get("week_title"),
                "planned_hours": checkin_data.get("planned_hours"),
                "planned_tasks_count": checkin_data.get("planned_tasks_count"),
                "task_list": checkin_data.get("tasks", [])
            },
            "student_checkin": {
                "actual_hours_spent": checkin_data.get("hours_spent", 0.0),
                "accomplishments": checkin_data.get("accomplishments", ""),
                "problems_faced": checkin_data.get("problems_faced", ""),
                "difficulty_level": checkin_data.get("difficulty_level", "moderate"),
                "self_rating": checkin_data.get("self_rating", 5),
                "notes": checkin_data.get("notes")
            },
            "factual_calculated_metrics": {
                "task_completion_pct": progress.get("task_completion_pct", 0.0),
                "time_completion_pct": progress.get("time_completion_pct", 0.0),
                "consistency_pct": progress.get("consistency_pct", 0.0),
                "completed_tasks": progress.get("completed_tasks", 0),
                "delayed_tasks": progress.get("delayed_tasks", 0),
                "streak": progress.get("streak", 0)
            },
            "previous_checkin_context": checkin_data.get("previous_context")
        }

        return self._call_groq(
            instruction=WEEKLY_ANALYSIS_INSTRUCTION,
            user_data=payload,
            schema_cls=AnalysisResult
        )

    def suggest_adjustment(
        self,
        analysis: Dict[str, Any],
        roadmap: Dict[str, Any],
        remaining_weeks: int
    ) -> AdjustmentSuggestion:
        adjustment_type = analysis.get("roadmap_adjustment_type") or analysis.get("type", "none")
        details = analysis.get("adjustment_details") or {"action": "maintain_pace", "target": "next_week"}

        return AdjustmentSuggestion(
            adjustment_type=adjustment_type,
            details=details
        )

    def generate_monthly_summary(
        self,
        goal: Dict[str, Any],
        checkins: List[Dict[str, Any]],
        progress_records: List[Dict[str, Any]]
    ) -> MonthlySummary:
        payload = {
            "goal": {
                "title": goal.get("name") or goal.get("title", ""),
                "category": str(goal.get("category", "")),
                "target_outcome": goal.get("target_outcome", "")
            },
            "total_checkins_logged": len(checkins),
            "checkin_summaries": [
                {
                    "week_id": str(c.get("week_id")),
                    "hours_spent": c.get("hours_spent", 0.0),
                    "tasks_completed": c.get("completed_tasks", 0),
                    "self_rating": c.get("self_rating", 5),
                    "accomplishments": c.get("accomplishments", ""),
                    "problems": c.get("problems", "")
                }
                for c in checkins
            ],
            "progress_records": [
                {
                    "week_number": pr.get("week_number"),
                    "task_completion_pct": pr.get("task_completion_pct", 0.0),
                    "time_completion_pct": pr.get("time_completion_pct", 0.0),
                    "consistency_pct": pr.get("consistency_pct", 0.0)
                }
                for pr in progress_records
            ]
        }

        return self._call_groq(
            instruction=MONTHLY_SUMMARY_INSTRUCTION,
            user_data=payload,
            schema_cls=MonthlySummary
        )
