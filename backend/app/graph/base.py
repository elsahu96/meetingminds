from __future__ import annotations

from app.graph.prompts import prompts

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class BaseAgent:

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    def __init__(self):
        openai_model_configs = dict(
            model=self.model_name,
            temperature=0,
            seed=1
        )
        self.model = ChatOpenAI(**openai_model_configs)

        self.prompt_template = ChatPromptTemplate.from_messages(
            prompts[self.prompt_name]["messages"]
        )






