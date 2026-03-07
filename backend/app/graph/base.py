from __future__ import annotations

from app.graph.prompts import prompts

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import get_settings


class BaseAgent:

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    def __init__(self):
        settings = get_settings()
        openai_model_configs = dict(model=self.model_name, temperature=0, seed=1, api_key=settings.openai_api_key)
        self.model = ChatOpenAI(**openai_model_configs)

        raw_messages = prompts[self.prompt_name]["messages"]
        # LangChain expects (role, content) tuples, not dicts
        messages = [(m["role"], m["content"]) for m in raw_messages]
        self.prompt_template = ChatPromptTemplate.from_messages(messages)
