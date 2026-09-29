from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import Optional, List

INSECURE_SECRET_PLACEHOLDERS = {
    "your-super-secret-key-change-in-production",
    "your_super_secret_key_minimum_32_characters_here",
    "change_me_to_a_random_32_byte_secret",
    "dev-insecure-secret-key-for-local-development-only-32chars",
    "changeme",
    "secret",
    "secretkey",
}


class Settings(BaseSettings):
    # Database connection URL (supports PostgreSQL and SQLite fallback for local development)
    DATABASE_URL: str = "sqlite:///./lifetrack.db"

    # PostgreSQL Connection Pool Configuration
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # Recycle connections after 30 minutes

    # JWT Authentication
    SECRET_KEY: str = "dev-insecure-secret-key-for-local-development-only-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS Configuration
    ALLOWED_ORIGINS: Optional[str] = None

    # Google OAuth 2.0 Credentials (Backend Only - Never exposed to frontend)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    ENABLE_OAUTH_MOCK: bool = False

    # AI Multi-Provider Configuration
    AI_PROVIDER: str = "openai"  # "openai" | "gemini" | "groq"
    AI_FALLBACK_PROVIDERS: Optional[str] = None

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-5.6-luna"
    AI_API_KEY: Optional[str] = None

    # Google Gemini Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Groq Settings
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    @property
    def effective_openai_api_key(self) -> Optional[str]:
        return self.OPENAI_API_KEY or self.AI_API_KEY

    @property
    def fallback_provider_list(self) -> List[str]:
        if not self.AI_FALLBACK_PROVIDERS:
            return []
        raw_list = [p.strip().lower() for p in self.AI_FALLBACK_PROVIDERS.split(",") if p.strip()]
        primary = (self.AI_PROVIDER or "").strip().lower()
        seen = set()
        clean = []
        for p in raw_list:
            if p != primary and p not in seen:
                seen.add(p)
                clean.append(p)
        return clean

    @property
    def cors_origins(self) -> List[str]:
        origins = []
        if self.ALLOWED_ORIGINS:
            origins.extend([o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()])
        if self.FRONTEND_URL and self.FRONTEND_URL.strip() not in origins:
            origins.append(self.FRONTEND_URL.strip())
        
        # Include standard local development ports when not in strict production or if origins empty
        if self.ENVIRONMENT.lower() != "production" or not origins:
            for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
                if dev_origin not in origins:
                    origins.append(dev_origin)
        return origins

    @property
    def cors_origin_regex(self) -> Optional[str]:
        # Only permit broad regex in local development environments
        if self.ENVIRONMENT.lower() != "production":
            return r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
        return None

    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        norm = (v or "").strip().lower()
        valid = {"openai", "gemini", "groq"}
        if norm not in valid:
            raise ValueError(f"AI_PROVIDER must be one of {valid}. Received '{v}'")
        return norm

    @field_validator("AI_FALLBACK_PROVIDERS")
    @classmethod
    def validate_fallback_providers(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        valid = {"openai", "gemini", "groq"}
        providers = [p.strip().lower() for p in v.split(",") if p.strip()]
        for p in providers:
            if p not in valid:
                raise ValueError(f"Unknown provider in AI_FALLBACK_PROVIDERS: '{p}'. Must be in {valid}")
        return v

    # Environment
    ENVIRONMENT: str = "development"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if not v or v.strip() == "":
            return "sqlite:///./lifetrack.db"
        v = v.strip()
        # Normalize postgres:// to postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        # Ensure standard driver postgresql+psycopg:// for SQLAlchemy 2.0 if bare postgresql:// provided
        if v.startswith("postgresql://") and not v.startswith("postgresql+"):
            v = v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        env = (self.ENVIRONMENT or "").strip().lower()
        secret = (self.SECRET_KEY or "").strip()

        if env == "production":
            if not secret:
                raise ValueError("SECRET_KEY is required and cannot be empty in production.")
            
            clean_secret = secret.lower()
            if clean_secret in INSECURE_SECRET_PLACEHOLDERS or clean_secret.startswith("change_me"):
                raise ValueError(
                    "SECRET_KEY is configured with an insecure placeholder or default. "
                    "Production requires a strong, high-entropy secret key."
                )

            if len(secret) < 32:
                raise ValueError(
                    "SECRET_KEY does not meet the minimum entropy requirements for production "
                    "(must be at least 32 characters / 256 bits)."
                )
        elif not secret:
            raise ValueError("SECRET_KEY cannot be empty.")

        # Ensure GOOGLE_REDIRECT_URI is derived from FRONTEND_URL if not explicitly configured
        if not self.GOOGLE_REDIRECT_URI or not self.GOOGLE_REDIRECT_URI.strip():
            base = (self.FRONTEND_URL or "http://localhost:3000").rstrip("/")
            self.GOOGLE_REDIRECT_URI = f"{base}/auth/callback/google"
        else:
            self.GOOGLE_REDIRECT_URI = self.GOOGLE_REDIRECT_URI.strip().rstrip("/")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
