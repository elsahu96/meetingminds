from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

    # SurrealDB
    surrealdb_url: str = "wss://brave-galaxy-06ebtcqtnhtov5ucd6f1tflbls.aws-euw1.surreal.cloud"
    surrealdb_namespace: str = "main"
    surrealdb_database: str = "main"
    surrealdb_user: str = "admin"
    surrealdb_pass: str = "admin"

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
