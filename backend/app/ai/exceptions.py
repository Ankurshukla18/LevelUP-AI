from fastapi import HTTPException


class AIServiceException(HTTPException):
    """
    Standard base exception raised by all AI provider operations.
    Translates provider and validation errors into user-safe HTTP status codes and messages.
    """
    def __init__(self, status_code: int = 502, detail: str = "AI service encountered an error."):
        super().__init__(status_code=status_code, detail=detail)


class AIProviderError(AIServiceException):
    """General provider-level failure."""
    def __init__(self, detail: str = "AI provider encountered an error."):
        super().__init__(status_code=502, detail=detail)


class AIAuthenticationError(AIServiceException):
    """Provider API key or authentication failed."""
    def __init__(self, detail: str = "AI provider authentication failed. Invalid API key."):
        super().__init__(status_code=502, detail=detail)


class AIRateLimitError(AIServiceException):
    """Provider rate limit or credit quota exceeded."""
    def __init__(self, detail: str = "AI rate limit or credit quota exceeded. Please check billing."):
        super().__init__(status_code=429, detail=detail)


class AITimeoutError(AIServiceException):
    """Provider request timed out."""
    def __init__(self, detail: str = "AI service request timed out."):
        super().__init__(status_code=504, detail=detail)


class AIConnectionError(AIServiceException):
    """Network connection to provider failed."""
    def __init__(self, detail: str = "Unable to connect to AI provider."):
        super().__init__(status_code=503, detail=detail)


class AIResponseValidationError(AIServiceException):
    """Model output failed JSON parsing or Pydantic schema validation."""
    def __init__(self, detail: str = "AI returned a response that failed strict application schema validation."):
        super().__init__(status_code=502, detail=detail)


class AIConfigurationError(AIServiceException):
    """Required provider API key or configuration missing."""
    def __init__(self, detail: str = "AI provider configuration or API key is missing."):
        super().__init__(status_code=503, detail=detail)
