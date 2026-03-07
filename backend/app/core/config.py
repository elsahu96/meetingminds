from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # SurrealDB
    surrealdb_url: str = os.getenv(
        "SURREALDB_URL",
        "wss://brave-galaxy-06ebtcqtnhtov5ucd6f1tflbls.aws-euw1.surreal.cloud/rpc",
    )
    surrealdb_namespace: str = os.getenv("SURREALDB_NAMESPACE", "main")
    surrealdb_database: str = os.getenv("SURREALDB_DATABASE", "main")
    surrealdb_user: str = os.getenv("SURREALDB_USER", "admin")
    surrealdb_pass: str = os.getenv("SURREALDB_PASS", "admin")
    # LangSmith
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "true")
    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "MeetingMinds")
    langsmith_endpoint: str = os.getenv(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )

    # App
    env: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
