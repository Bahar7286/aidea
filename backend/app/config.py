from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./agritwin.db"
    secret_key: str = "agritwin-dev-secret-change-in-production"
    access_token_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:3000"
    algorithm: str = "HS256"
    # Optional: hybrid AI explanations via OpenRouter (rules stay safety floor)
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    # Upsert demo users on startup: "1" force on, "0" force off; empty = auto on Postgres
    seed_demo_users: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
