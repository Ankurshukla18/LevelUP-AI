from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List
from datetime import date, datetime
import uuid
from ..models.goal import GoalCategory, GoalPriority, GoalStatus


class GoalBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: GoalCategory
    description: Optional[str] = Field(default=None, max_length=5000)
    start_date: date
    target_date: date
    current_level: str = Field(min_length=1, max_length=100)
    target_outcome: str = Field(min_length=1, max_length=2000)
    available_hours_per_week: float = Field(gt=0, le=168)
    priority: GoalPriority = GoalPriority.medium
    motivation: Optional[str] = Field(default=None, max_length=5000)
    preferred_days: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "GoalBase":
        if self.target_date < self.start_date:
            raise ValueError("Target date cannot be before start date.")
        return self

    @model_validator(mode="before")
    @classmethod
    def map_camel_and_enums(cls, values: dict):
        if not isinstance(values, dict):
            return values

        data = values.copy()
        # Map camelCase to snake_case if present
        if "startDate" in data and "start_date" not in data:
            data["start_date"] = data.pop("startDate")
        if "targetDate" in data and "target_date" not in data:
            data["target_date"] = data.pop("targetDate")
        if "currentLevel" in data and "current_level" not in data:
            data["current_level"] = data.pop("currentLevel")
        if "targetOutcome" in data and "target_outcome" not in data:
            data["target_outcome"] = data.pop("targetOutcome")
        if "availableHoursPerWeek" in data and "available_hours_per_week" not in data:
            data["available_hours_per_week"] = data.pop("availableHoursPerWeek")
        if "preferredDays" in data and "preferred_days" not in data:
            data["preferred_days"] = data.pop("preferredDays")

        # Normalize category
        if "category" in data and isinstance(data["category"], str):
            norm_cat = data["category"].strip().lower().replace(" ", "_")
            data["category"] = norm_cat

        # Normalize priority
        if "priority" in data and isinstance(data["priority"], str):
            norm_prio = data["priority"].strip().lower()
            data["priority"] = norm_prio

        return data


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[GoalCategory] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    current_level: Optional[str] = None
    target_outcome: Optional[str] = None
    available_hours_per_week: Optional[float] = None
    priority: Optional[GoalPriority] = None
    motivation: Optional[str] = None
    preferred_days: Optional[List[str]] = None
    status: Optional[GoalStatus] = None

    @model_validator(mode="before")
    @classmethod
    def map_camel_case_update(cls, values: dict):
        if not isinstance(values, dict):
            return values
        data = values.copy()
        if "startDate" in data:
            data["start_date"] = data.pop("startDate")
        if "targetDate" in data:
            data["target_date"] = data.pop("targetDate")
        if "currentLevel" in data:
            data["current_level"] = data.pop("currentLevel")
        if "targetOutcome" in data:
            data["target_outcome"] = data.pop("targetOutcome")
        if "availableHoursPerWeek" in data:
            data["available_hours_per_week"] = data.pop("availableHoursPerWeek")
        if "category" in data and isinstance(data["category"], str):
            data["category"] = data["category"].strip().lower().replace(" ", "_")
        if "priority" in data and isinstance(data["priority"], str):
            data["priority"] = data["priority"].strip().lower()
        return data


class GoalResponse(GoalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
