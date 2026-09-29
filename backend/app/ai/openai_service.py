import json
import logging
from typing import Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
import openai
from openai import OpenAI

from ..config import settings
from .base import AIProvider
from .schemas import (
    RoadmapData,
    WeekGen,
    TaskGen,
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


class OpenAIService(AIProvider):
    """
    Production AI Service communicating with official OpenAI Python SDK.
    Uses Responses API with graceful fallback to Chat Completions.
    Strictly validates outputs against Pydantic schemas.
    """

    provider_name: str = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.effective_openai_api_key
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-5.6-luna")
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if not self.api_key:
            raise AIConfigurationError(
                detail="OpenAI API key is not configured. Please set OPENAI_API_KEY in the backend environment."
            )
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _clean_json_text(self, text: str) -> str:
        """Strip surrounding markdown codeblocks if model inadvertently added them."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _call_openai(self, instruction: str, user_data: Dict[str, Any], schema_cls: Type[T]) -> T:
        """
        Executes call to OpenAI using Responses API with structured schema validation.
        Protects against prompt injection by separating system instructions from user data payload.
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

        # 1. Primary Attempt: OpenAI Responses API
        try:
            logger.info(f"Calling OpenAI Responses API with model: {self.model}")
            response = self.client.responses.create(
                model=self.model,
                instructions=full_system_instruction,
                input=formatted_prompt
            )
            raw_output_text = response.output_text
        except openai.AuthenticationError as err:
            logger.error(f"OpenAI Authentication Error: {err}")
            raise AIAuthenticationError(
                detail="OpenAI authentication failed. Invalid API key provided in server configuration."
            ) from err
        except openai.RateLimitError as err:
            logger.error(f"OpenAI Rate Limit / Quota Error: {err}")
            raise AIRateLimitError(
                detail="OpenAI rate limit or credit quota exceeded. Please check your OpenAI account billing."
            ) from err
        except openai.APITimeoutError as err:
            logger.error(f"OpenAI Timeout Error: {err}")
            raise AITimeoutError(
                detail="OpenAI API request timed out. Please try again in a few moments."
            ) from err
        except openai.APIConnectionError as err:
            logger.error(f"OpenAI Connection Error: {err}")
            raise AIConnectionError(
                detail="Unable to reach OpenAI API service. Please verify server internet connectivity."
            ) from err
        except (openai.BadRequestError, openai.NotFoundError) as err:
            # Model may not be supported on Responses API endpoint yet; fallback to Chat Completions
            logger.warning(f"Responses API error ({err}), falling back to Chat Completions API with model {self.model}...")
            try:
                chat_res = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": full_system_instruction},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                if chat_res.choices and chat_res.choices[0].message:
                    raw_output_text = chat_res.choices[0].message.content
            except openai.RateLimitError as rle:
                raise AIRateLimitError(
                    detail="OpenAI rate limit or credit quota exceeded. Please check your OpenAI account billing."
                ) from rle
            except openai.AuthenticationError as ae:
                raise AIAuthenticationError(
                    detail="OpenAI authentication failed. Invalid API key provided in server configuration."
                ) from ae
            except Exception as e:
                safe_e = self.sanitize_error(str(e))
                logger.error(f"Chat Completions fallback failed: {safe_e}")
                raise AIProviderError(
                    detail=f"OpenAI API call failed: {safe_e}"
                ) from e
        except openai.APIError as err:
            safe_err = self.sanitize_error(err.message if hasattr(err, 'message') else str(err))
            logger.error(f"OpenAI General API Error: {safe_err}")
            raise AIProviderError(
                detail=f"OpenAI API error: {safe_err}"
            ) from err

        if not raw_output_text:
            raise AIResponseValidationError(
                detail="OpenAI returned an empty response."
            )

        # 2. Strict Schema Validation
        cleaned_text = self._clean_json_text(raw_output_text)
        try:
            parsed_data = json.loads(cleaned_text)
            validated_object = schema_cls.model_validate(parsed_data)
            return validated_object
        except (json.JSONDecodeError, ValidationError) as val_err:
            logger.error(f"Structured response validation failed: {val_err}. Raw output was: {raw_output_text[:300]}")
            raise AIResponseValidationError(
                detail="OpenAI returned a response that failed strict application schema validation."
            ) from val_err

    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        """
        Generates realistic weekly roadmap from user's goal information.
        Does NOT invent progress; strictly creates a step-by-step plan.
        """
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

        return self._call_openai(
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
        """
        Analyzes student performance for a completed week based strictly on factual metrics.
        """
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

        return self._call_openai(
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
        """
        Recommends roadmap adaptation parameters based on verified performance bottleneck.
        """
        adjustment_type = analysis.get("roadmap_adjustment_type") or analysis.get("type", "none")
        details = analysis.get("adjustment_details") or {"action": "maintain_pace", "target": "next_week"}

        return AdjustmentSuggestion(
            adjustment_type=adjustment_type,
            details=details
        )

    def generate_monthly_summary(
        self,
        goal: Dict[str, Any],
        checkins: list,
        progress_records: list
    ) -> MonthlySummary:
        """
        Produces factual monthly retrospective across all logged check-ins.
        """
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

        return self._call_openai(
            instruction=MONTHLY_SUMMARY_INSTRUCTION,
            user_data=payload,
            schema_cls=MonthlySummary
        )
