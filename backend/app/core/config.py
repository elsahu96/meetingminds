from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI
    openai_api_key: str = ""

    # SurrealDB
    surrealdb_url: str = "ws://localhost:8000/rpc"
    surrealdb_namespace: str = "meetingmind"
    surrealdb_database: str = "main"
    surrealdb_user: str = "root"
    surrealdb_pass: str = "root"

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "meetingmind"

    # App
    env: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
