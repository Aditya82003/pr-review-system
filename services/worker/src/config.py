# it contains basically  the env file for the worker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_app_id: str=""
    github_app_private_key_path: str=""
    github_webhook_secret: str=""

    anthropic_api_key: str = ""
    review_model: str = "claude-sonnet-4-6"

    redis_url: str = "redis://redis:6379/0"
    database_url: str = "postgresql+psycopg://postgres:aditya@localhost:5432/pr_review"

    orchestrator_callback_url: str = "http://orchestrator:8080/internal/review-callback"
    sandbox_image: str = "pr-review/reviewer-sandbox:latest"

    auto_post_threshold: float = 0.85
    suggest_threshold: float = 0.6

    class Config:
        env_file = ".env"


settings = Settings()
