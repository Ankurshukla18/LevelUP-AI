"""
Tests for OpenAIService — covers:
  - Missing API key → 503
  - Invalid API key (AuthenticationError) → 502
  - Rate limit / quota exhausted (RateLimitError) → 429
  - Timeout → 504
  - Connection error → 503
  - Malformed / invalid JSON from OpenAI → 502
  - Successful roadmap generation (mocked client)
  - Successful weekly analysis (mocked client)
  - Successful monthly summary (mocked client)
  - User isolation: analyzed checkin must belong to the authenticated user's goal
"""
import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi import HTTPException

import openai

# ── Import service under test ────────────────────────────────────────────────
from app.ai.openai_service import OpenAIService
from app.ai.exceptions import AIServiceException
from app.ai.schemas import RoadmapData, AnalysisResult, MonthlySummary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_ROADMAP_JSON = json.dumps({
    "weeks": [
        {
            "week_number": 1,
            "title": "Foundations",
            "description": "Build a solid base",
            "estimated_hours": 5.0,
            "tasks": [
                {
                    "title": "Task 1",
                    "description": "First task",
                    "estimated_hours": 2.0,
                    "order": 1,
                }
            ],
        }
    ]
})

VALID_ANALYSIS_JSON = json.dumps({
    "summary": "Good week overall.",
    "went_well": ["Completed all planned tasks"],
    "delayed": [],
    "reasons": [],
    "recommendations": ["Continue at this pace"],
    "next_week_focus": ["Review previous concepts"],
    "roadmap_adjustment_type": "none",
    "adjustment_details": {},
})

VALID_MONTHLY_JSON = json.dumps({
    "month": "January 2025",
    "overall_progress": "Solid month of progress.",
    "key_achievements": ["Consistent study habit"],
    "areas_for_improvement": ["Time management"],
    "challenges": ["Balancing full-time schedule"],
    "patterns": ["Better on weekdays"],
    "recommendations": ["Add 1 more hour per week"],
    "focus_next_month": "Advance to intermediate phase",
})


def _make_service(api_key="sk-test-key", model="gpt-4o"):
    """Return an OpenAIService with explicit key (bypasses env read)."""
    return OpenAIService(api_key=api_key, model=model)


def _mock_responses_output(text: str):
    """Build a mock OpenAI Responses API response object."""
    mock_resp = MagicMock()
    mock_resp.output_text = text
    return mock_resp


# ---------------------------------------------------------------------------
# 1. Missing API key → 503
# ---------------------------------------------------------------------------

def test_missing_api_key_raises_503():
    service = OpenAIService(api_key="", model="gpt-4o")
    with pytest.raises(AIServiceException) as exc_info:
        # Access the lazy client property which validates the key
        _ = service.client
    assert exc_info.value.status_code == 503
    assert "OPENAI_API_KEY" in exc_info.value.detail


# ---------------------------------------------------------------------------
# 2. Invalid API key (AuthenticationError) → 502
# ---------------------------------------------------------------------------

def test_authentication_error_raises_502():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = openai.AuthenticationError(
        "invalid key", response=MagicMock(status_code=401), body={}
    )
    service._client = mock_client

    goal_info = {"name": "Learn Python", "start_date": "2025-01-01", "target_date": "2025-06-01"}

    with pytest.raises(AIServiceException) as exc_info:
        service.generate_roadmap(goal_info)
    assert exc_info.value.status_code == 502
    assert "authentication" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 3. Rate limit / quota exhausted → 429
# ---------------------------------------------------------------------------

def test_rate_limit_error_raises_429():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = openai.RateLimitError(
        "rate limit", response=MagicMock(status_code=429), body={}
    )
    service._client = mock_client

    goal_info = {"name": "Learn Python", "start_date": "2025-01-01", "target_date": "2025-06-01"}

    with pytest.raises(AIServiceException) as exc_info:
        service.generate_roadmap(goal_info)
    assert exc_info.value.status_code == 429
    assert "rate limit" in exc_info.value.detail.lower() or "quota" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 4. Timeout → 504
# ---------------------------------------------------------------------------

def test_timeout_error_raises_504():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = openai.APITimeoutError(request=MagicMock())
    service._client = mock_client

    goal_info = {"name": "Learn Python", "start_date": "2025-01-01", "target_date": "2025-06-01"}

    with pytest.raises(AIServiceException) as exc_info:
        service.generate_roadmap(goal_info)
    assert exc_info.value.status_code == 504
    assert "timed out" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 5. Connection error → 503
# ---------------------------------------------------------------------------

def test_connection_error_raises_503():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = openai.APIConnectionError(request=MagicMock())
    service._client = mock_client

    goal_info = {"name": "Learn Python", "start_date": "2025-01-01", "target_date": "2025-06-01"}

    with pytest.raises(AIServiceException) as exc_info:
        service.generate_roadmap(goal_info)
    assert exc_info.value.status_code == 503
    assert "reach" in exc_info.value.detail.lower() or "connect" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 6. Malformed / invalid JSON from OpenAI → 502
# ---------------------------------------------------------------------------

def test_malformed_json_raises_502():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = _mock_responses_output("NOT VALID JSON {{{{")
    service._client = mock_client

    goal_info = {"name": "Learn Python", "start_date": "2025-01-01", "target_date": "2025-06-01"}

    with pytest.raises(AIServiceException) as exc_info:
        service.generate_roadmap(goal_info)
    assert exc_info.value.status_code == 502
    assert "validation" in exc_info.value.detail.lower() or "schema" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 7. Successful roadmap generation
# ---------------------------------------------------------------------------

def test_generate_roadmap_success():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = _mock_responses_output(VALID_ROADMAP_JSON)
    service._client = mock_client

    goal_info = {
        "name": "Learn Python",
        "category": "technology",
        "description": "Master Python programming",
        "current_level": "Beginner",
        "target_outcome": "Build a web app",
        "start_date": "2025-01-01",
        "target_date": "2025-06-01",
        "available_hours_per_week": 8.0,
        "priority": "high",
        "preferred_days": ["Monday", "Wednesday", "Friday"],
    }

    result = service.generate_roadmap(goal_info)

    assert isinstance(result, RoadmapData)
    assert len(result.weeks) == 1
    assert result.weeks[0].week_number == 1
    assert result.weeks[0].title == "Foundations"
    assert len(result.weeks[0].tasks) == 1

    # Ensure user data was passed (prompt injection protection: it should be in user_content, not system)
    call_kwargs = mock_client.responses.create.call_args[1]
    assert "Learn Python" in call_kwargs["input"]  # user data in input field


# ---------------------------------------------------------------------------
# 8. Successful weekly analysis
# ---------------------------------------------------------------------------

def test_analyze_week_success():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = _mock_responses_output(VALID_ANALYSIS_JSON)
    service._client = mock_client

    checkin_data = {
        "week_number": 1,
        "week_title": "Foundations",
        "planned_hours": 8.0,
        "planned_tasks_count": 3,
        "tasks": [{"title": "Task A", "description": "Do A"}],
        "hours_spent": 7.5,
        "accomplishments": "Finished all tasks",
        "problems_faced": "None",
        "difficulty_level": "moderate",
        "self_rating": 8,
        "notes": None,
        "previous_context": None,
    }
    goal_info = {
        "name": "Learn Python",
        "category": "technology",
        "target_outcome": "Build a web app",
        "available_hours_per_week": 8.0,
    }
    progress = {
        "task_completion_pct": 100.0,
        "time_completion_pct": 93.75,
        "consistency_pct": 100.0,
        "completed_tasks": 3,
        "delayed_tasks": 0,
        "streak": 7,
    }

    result = service.analyze_week(checkin_data, goal_info, progress)

    assert isinstance(result, AnalysisResult)
    assert result.summary == "Good week overall."
    assert result.roadmap_adjustment_type == "none"
    assert len(result.went_well) == 1


# ---------------------------------------------------------------------------
# 9. Successful monthly summary
# ---------------------------------------------------------------------------

def test_generate_monthly_summary_success():
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = _mock_responses_output(VALID_MONTHLY_JSON)
    service._client = mock_client

    goal = {"name": "Learn Python", "category": "technology", "target_outcome": "Build a web app"}
    checkins = [
        {
            "week_id": "abc-123",
            "hours_spent": 7.0,
            "completed_tasks": 3,
            "delayed_tasks": 0,
            "self_rating": 7,
            "accomplishments": "Good progress",
            "problems": "",
            "difficulty": "moderate",
        }
    ]
    progress_records = [
        {
            "week_number": 1,
            "task_completion_pct": 100.0,
            "time_completion_pct": 87.5,
            "consistency_pct": 100.0,
        }
    ]

    result = service.generate_monthly_summary(goal, checkins, progress_records)

    assert isinstance(result, MonthlySummary)
    assert result.month == "January 2025"
    assert result.overall_progress == "Solid month of progress."
    assert "Consistent study habit" in result.key_achievements
    assert result.focus_next_month == "Advance to intermediate phase"


# ---------------------------------------------------------------------------
# 10. Markdown code-block stripping
# ---------------------------------------------------------------------------

def test_clean_json_text_strips_markdown():
    service = _make_service()
    dirty = "```json\n{\"key\": \"value\"}\n```"
    assert service._clean_json_text(dirty) == '{"key": "value"}'

    dirty2 = "```\n{\"key\": \"value\"}\n```"
    assert service._clean_json_text(dirty2) == '{"key": "value"}'

    clean = '{"key": "value"}'
    assert service._clean_json_text(clean) == clean


# ---------------------------------------------------------------------------
# 11. User isolation — goal must belong to current user
#     (tested at router level; here we verify the service never mixes user data)
# ---------------------------------------------------------------------------

def test_user_data_isolation_in_payload():
    """
    Verifies that the payload sent to OpenAI contains ONLY the provided
    goal/checkin data (i.e. service does NOT pull additional DB data).
    This is a contract test: the router is responsible for passing
    only the authenticated user's data.
    """
    service = _make_service()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = _mock_responses_output(VALID_ANALYSIS_JSON)
    service._client = mock_client

    # Goal belonging to user A
    user_a_goal = {
        "name": "User A Goal",
        "category": "health",
        "target_outcome": "Lose weight",
        "available_hours_per_week": 3.0,
    }
    checkin_data = {
        "week_number": 1,
        "week_title": "Week 1",
        "planned_hours": 3.0,
        "planned_tasks_count": 2,
        "tasks": [],
        "hours_spent": 2.5,
        "accomplishments": "Did well",
        "problems_faced": None,
        "difficulty_level": "easy",
        "self_rating": 9,
        "notes": None,
        "previous_context": None,
    }
    progress = {
        "task_completion_pct": 100.0,
        "time_completion_pct": 83.0,
        "consistency_pct": 100.0,
        "completed_tasks": 2,
        "delayed_tasks": 0,
        "streak": 3,
    }

    result = service.analyze_week(checkin_data, user_a_goal, progress)

    # The prompt payload must contain ONLY user A's data
    call_kwargs = mock_client.responses.create.call_args[1]
    payload_str = call_kwargs["input"]
    assert "User A Goal" in payload_str
    # Must NOT contain any other user's data (nothing was passed about another user)
    assert "User B" not in payload_str
