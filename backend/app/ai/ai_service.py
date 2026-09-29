from abc import ABC, abstractmethod
from typing import Dict, Any
from .schemas import RoadmapData, AnalysisResult, AdjustmentSuggestion, MonthlySummary

class AIService(ABC):
    @abstractmethod
    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        pass

    @abstractmethod
    def analyze_week(self, checkin_data: Dict[str, Any], goal_info: Dict[str, Any], progress: Dict[str, Any]) -> AnalysisResult:
        pass

    @abstractmethod
    def suggest_adjustment(self, analysis: Dict[str, Any], roadmap: Dict[str, Any], remaining_weeks: int) -> AdjustmentSuggestion:
        pass

    @abstractmethod
    def generate_monthly_summary(self, goal: Dict[str, Any], checkins: list, progress_records: list) -> MonthlySummary:
        pass
