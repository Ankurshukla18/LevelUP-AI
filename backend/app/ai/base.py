from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .ai_service import AIService
from .schemas import RoadmapData, AnalysisResult, AdjustmentSuggestion, MonthlySummary


class AIProvider(AIService, ABC):
    """
    Provider-independent interface for LifeTrack AI services.
    Enforces standardized Pydantic model outputs across all LLM providers (OpenAI, Gemini, Groq).
    """

    provider_name: str = "base"
    model: str = "default"

    @abstractmethod
    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        """Generates realistic weekly roadmap from user's goal information."""
        pass

    @abstractmethod
    def analyze_week(
        self,
        checkin_data: Dict[str, Any],
        goal_info: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> AnalysisResult:
        """Analyzes student performance for a completed week based on factual metrics."""
        pass

    @abstractmethod
    def suggest_adjustment(
        self,
        analysis: Dict[str, Any],
        roadmap: Dict[str, Any],
        remaining_weeks: int
    ) -> AdjustmentSuggestion:
        """Recommends roadmap adaptation parameters based on verified bottlenecks."""
        pass

    @abstractmethod
    def generate_monthly_summary(
        self,
        goal: Dict[str, Any],
        checkins: List[Dict[str, Any]],
        progress_records: List[Dict[str, Any]]
    ) -> MonthlySummary:
        """Produces factual monthly retrospective across all logged check-ins."""
        pass

    # Aliases for flexible method invocation
    def analyze_progress(
        self,
        checkin_data: Dict[str, Any],
        goal_info: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> AnalysisResult:
        return self.analyze_week(checkin_data, goal_info, progress)

    def adjust_roadmap(
        self,
        analysis: Dict[str, Any],
        roadmap: Dict[str, Any],
        remaining_weeks: int
    ) -> AdjustmentSuggestion:
        return self.suggest_adjustment(analysis, roadmap, remaining_weeks)

    def generate_monthly_review(
        self,
        goal: Dict[str, Any],
        checkins: List[Dict[str, Any]],
        progress_records: List[Dict[str, Any]]
    ) -> MonthlySummary:
        return self.generate_monthly_summary(goal, checkins, progress_records)

    @staticmethod
    def clean_json_text(text: str) -> str:
        """Strips surrounding markdown codeblocks if model inadvertently added them."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def sanitize_error(self, err_message: str) -> str:
        """Sanitizes error messages removing API keys or sensitive authorization tokens."""
        if not err_message:
            return ""
        sanitized = str(err_message)
        api_key = getattr(self, "api_key", None)
        if api_key and len(str(api_key)) > 4:
            sanitized = sanitized.replace(str(api_key), "[REDACTED]")
        return sanitized


clean_json_text = AIProvider.clean_json_text
