from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_file_encoding="utf-8"
    )

    # Apify
    apify_api_key: str
    apify_actor_id: str = "apify/google-maps-scraper"
    apify_timeout_seconds: int = 300

    # LLM
    google_api_key: str
    llm_model: str = "gemini-2.0-flash"

    # Stripe
    # stripe_secret_key: str
    # stripe_publishable_key: str
    # stripe_webhook_secret: str
    # stripe_price_id: str

    # General
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
