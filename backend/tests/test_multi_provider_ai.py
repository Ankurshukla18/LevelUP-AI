"""
Tests for Multi-Provider AI Architecture:
- Provider selection (openai, gemini, groq, mock)
- Google Gemini provider implementation and schema validation
- Groq provider implementation and schema validation
- Bounded fallback chain:
  - Transient failure (429, 503, timeout) fails over to next provider
  - Non-transient failure (AIResponseValidationError) halts immediately without retry storm
  - All providers failing raises AIServiceException
- Security: secrets/keys never leaked in exception messages
"""
import json
import pytest
import httpx
from unittest.mock import MagicMock, patch

from app.ai.base import AIProvider, clean_json_text
from app.ai.exceptions import (
    AIServiceException,
    AIRateLimitError,
    AIConnectionError,
    AITimeoutError,
    AIAuthenticationError,
    AIResponseValidationError,
    AIConfigurationError,
)
from app.ai.schemas import RoadmapData, AnalysisResult, AdjustmentSuggestion, MonthlySummary
from app.ai.gemini_service import GeminiService
from app.ai.groq_service import GroqService
from app.ai.openai_service import OpenAIService
from app.ai.mock_ai_service import MockAIService
from app.ai.factory import get_ai_service, create_provider, FallbackChainService


# Sample payloads
SAMPLE_GOAL = {
    "name": "Master Python",
    "category": "Coding",
    "target_outcome": "Build production apps",
    "available_hours_per_week": 10.0,
}

VALID_ROADMAP_DICT = {
    "weeks": [
        {
            "week_number": 1,
            "title": "Syntax Fundamentals",
            "description": "Learn basic Python syntax and types",
            "estimated_hours": 10.0,
            "tasks": [
                {
                    "title": "Data Types and Variables",
                    "description": "Practice strings, ints, lists, dicts",
                    "estimated_hours": 5.0,
                    "order": 1,
                }
            ],
        }
    ]
}

VALID_ANALYSIS_DICT = {
    "summary": "Great progress this week.",
    "went_well": ["Completed data structures lab"],
    "delayed": [],
    "reasons": [],
    "recommendations": ["Start object-oriented programming next"],
    "next_week_focus": ["OOP basics"],
    "roadmap_adjustment_type": "none",
    "adjustment_details": {},
}

VALID_ADJUSTMENT_DICT = {
    "adjustment_type": "none",
    "reason": "On track with scheduled pace.",
    "details": {},
}

VALID_MONTHLY_DICT = {
    "month_label": "September 2026",
    "overall_score": 88,
    "highlights": ["Strong consistency"],
    "growth_areas": ["Increase weekend study"],
    "recommendations": ["Maintain momentum"],
}


# ===========================================================================
# 1. Clean JSON utility tests
# ===========================================================================
def test_clean_json_text():
    raw_markdown = "```json\n{\"key\": \"value\"}\n```"
    cleaned = clean_json_text(raw_markdown)
    assert json.loads(cleaned) == {"key": "value"}

    embedded = "```\n{\"test\": 123}\n```"
    assert json.loads(clean_json_text(embedded)) == {"test": 123}


# ===========================================================================
# 2. Gemini Service Tests
# ===========================================================================
def test_gemini_missing_api_key():
    service = GeminiService(api_key="")
    with pytest.raises(AIConfigurationError) as exc_info:
        _ = service.client
    assert exc_info.value.status_code == 503
    assert "GEMINI_API_KEY" in str(exc_info.value.detail)


def test_gemini_generate_roadmap_success():
    service = GeminiService(api_key="fake-gemini-key", model="gemini-2.5-flash")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps(VALID_ROADMAP_DICT)
    mock_client.models.generate_content.return_value = mock_response
    service._client = mock_client

    result = service.generate_roadmap(SAMPLE_GOAL)

    assert isinstance(result, RoadmapData)
    assert len(result.weeks) == 1
    assert result.weeks[0].title == "Syntax Fundamentals"
    mock_client.models.generate_content.assert_called_once()


def test_gemini_schema_validation_error():
    service = GeminiService(api_key="fake-gemini-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Invalid schema: missing required 'weeks' array
    mock_response.text = json.dumps({"wrong_key": 123})
    mock_client.models.generate_content.return_value = mock_response
    service._client = mock_client

    with pytest.raises(AIResponseValidationError) as exc_info:
        service.generate_roadmap(SAMPLE_GOAL)
    assert exc_info.value.status_code == 502
    assert "validation" in str(exc_info.value.detail).lower()


# ===========================================================================
# 3. Groq Service Tests
# ===========================================================================
def test_groq_missing_api_key():
    service = GroqService(api_key="")
    with pytest.raises(AIConfigurationError) as exc_info:
        _ = service.client
    assert exc_info.value.status_code == 503
    assert "GROQ_API_KEY" in str(exc_info.value.detail)


def test_groq_generate_roadmap_success():
    service = GroqService(api_key="fake-groq-key", model="llama-3.3-70b-versatile")
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(VALID_ROADMAP_DICT)
    mock_res = MagicMock()
    mock_res.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_res
    service._client = mock_client

    result = service.generate_roadmap(SAMPLE_GOAL)

    assert isinstance(result, RoadmapData)
    assert result.weeks[0].week_number == 1
    mock_client.chat.completions.create.assert_called_once()


def test_groq_rate_limit_error():
    import groq
    service = GroqService(api_key="fake-groq-key")
    mock_client = MagicMock()
    req = httpx.Request("POST", "https://api.groq.com")
    resp = httpx.Response(429, request=req)
    mock_client.chat.completions.create.side_effect = groq.RateLimitError(
        message="Rate limit reached", response=resp, body=None
    )
    service._client = mock_client

    with pytest.raises(AIRateLimitError) as exc_info:
        service.generate_roadmap(SAMPLE_GOAL)
    assert exc_info.value.status_code == 429


# ===========================================================================
# 4. Factory & Provider Instantiation Tests
# ===========================================================================
def test_create_provider_mock():
    prov = create_provider("mock")
    assert isinstance(prov, MockAIService)


def test_create_provider_unknown():
    with pytest.raises(AIConfigurationError):
        create_provider("unknown_provider")


@patch("app.ai.factory.settings")
def test_get_ai_service_standalone_when_no_fallbacks(mock_settings):
    mock_settings.AI_PROVIDER = "mock"
    mock_settings.AI_FALLBACK_PROVIDERS = ""
    mock_settings.fallback_provider_list = []

    service = get_ai_service()
    assert isinstance(service, MockAIService)


@patch("app.ai.factory.settings")
def test_get_ai_service_fallback_chain_when_configured(mock_settings):
    mock_settings.AI_PROVIDER = "mock"
    mock_settings.AI_FALLBACK_PROVIDERS = "mock"
    mock_settings.fallback_provider_list = ["mock"]

    service = get_ai_service()
    assert isinstance(service, FallbackChainService)


# ===========================================================================
# 5. Fallback Chain Behavior Tests
# ===========================================================================
class FailingMockProvider(AIProvider):
    provider_name = "failing_mock"
    model = "fail-v1"

    def __init__(self, exception_to_raise):
        self.exception_to_raise = exception_to_raise
        self.call_count = 0

    def generate_roadmap(self, goal_info):
        self.call_count += 1
        raise self.exception_to_raise

    def analyze_week(self, checkin_data, goal_info, progress):
        self.call_count += 1
        raise self.exception_to_raise

    def suggest_adjustment(self, analysis, roadmap, remaining_weeks):
        self.call_count += 1
        raise self.exception_to_raise

    def generate_monthly_summary(self, goal, checkins, progress_records):
        self.call_count += 1
        raise self.exception_to_raise


class SucceedingMockProvider(AIProvider):
    provider_name = "succeeding_mock"
    model = "success-v1"

    def __init__(self):
        self.call_count = 0

    def generate_roadmap(self, goal_info):
        self.call_count += 1
        return RoadmapData.model_validate(VALID_ROADMAP_DICT)

    def analyze_week(self, checkin_data, goal_info, progress):
        self.call_count += 1
        return AnalysisResult.model_validate(VALID_ANALYSIS_DICT)

    def suggest_adjustment(self, analysis, roadmap, remaining_weeks):
        self.call_count += 1
        return AdjustmentSuggestion.model_validate(VALID_ADJUSTMENT_DICT)

    def generate_monthly_summary(self, goal, checkins, progress_records):
        self.call_count += 1
        return MonthlySummary.model_validate(VALID_MONTHLY_DICT)


def test_fallback_chain_primary_succeeds():
    primary = SucceedingMockProvider()
    fallback = SucceedingMockProvider()

    chain = FallbackChainService(providers=[primary, fallback])
    res = chain.generate_roadmap(SAMPLE_GOAL)

    assert isinstance(res, RoadmapData)
    assert primary.call_count == 1
    assert fallback.call_count == 0


def test_fallback_chain_primary_transient_error_falls_back():
    primary = FailingMockProvider(AIRateLimitError("Primary rate limit"))
    fallback = SucceedingMockProvider()

    chain = FallbackChainService(providers=[primary, fallback])
    res = chain.generate_roadmap(SAMPLE_GOAL)

    assert isinstance(res, RoadmapData)
    assert primary.call_count == 1
    assert fallback.call_count == 1


def test_fallback_chain_no_retry_on_schema_validation_error():
    # Schema validation failure should halt immediately (prevent retry loops)
    primary = FailingMockProvider(AIResponseValidationError("Malformed schema response"))
    fallback = SucceedingMockProvider()

    chain = FallbackChainService(providers=[primary, fallback])
    with pytest.raises(AIResponseValidationError):
        chain.generate_roadmap(SAMPLE_GOAL)

    assert primary.call_count == 1
    assert fallback.call_count == 0  # Fallback must NOT be called


def test_fallback_chain_all_fail():
    primary = FailingMockProvider(AIRateLimitError("Primary 429"))
    fallback = FailingMockProvider(AIConnectionError("Secondary 503"))

    chain = FallbackChainService(providers=[primary, fallback])
    with pytest.raises(AIServiceException) as exc_info:
        chain.generate_roadmap(SAMPLE_GOAL)

    assert exc_info.value.status_code == 503
    assert primary.call_count == 1
    assert fallback.call_count == 1


# ===========================================================================
# 6. Security: API Keys Not Exposed
# ===========================================================================
def test_no_api_key_leakage_in_exceptions():
    fake_secret = "secret-key-12345-do-not-leak"
    service = GroqService(api_key=fake_secret)
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception(f"Internal failed with {fake_secret}")
    service._client = mock_client

    try:
        service.generate_roadmap(SAMPLE_GOAL)
    except AIServiceException as e:
        # The exception detail presented to API callers must not contain the raw secret
        assert fake_secret not in str(e.detail)
