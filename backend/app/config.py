from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./lifetrack.db"
    SECRET_KEY: str = "your-super-secret-key-keep-it-safe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AI_API_KEY: str = ""
    AI_PROVIDER: str = "mock"  # "mock" or "openai" etc.

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
