from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    environment: str = "development"
    app_name: str = "TrendFlare API"
    debug: bool = True

    # AI Keys
    gemini_api_key: str = ""
    hf_token: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "TrendFlare/1.0"

    # Ayrshare
    ayrshare_api_key: str = ""

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # Database
    database_url: str = "postgresql://trendflare:trendflare_dev@localhost:5432/trendflare"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Rate limits
    gemini_max_requests_per_day: int = 1500
    hf_request_timeout: int = 60

    model_config = {"env_file": "../../.env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
