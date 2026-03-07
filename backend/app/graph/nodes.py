from app.graph.base import BaseAgent
from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    type: str = Field(description="One of: Person, Team, Topic, Action")
    name: str = Field(description="Canonical name for the entity")
    description: str = Field(description="1-3 sentence summary")


class ExtractedEntities(BaseModel):
    """JSON array of extracted entities from a meeting transcript."""

    entities: list[ExtractedEntity] = Field(
        default_factory=list, description="List of extracted entities"
    )


class NodeExtrator(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    async def __call__(self, state: dict):
        transcript = state.get("transcript", "")
        prompt_vars = {"transcripts": transcript}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEntities)
        result = await llm.ainvoke(prompt)
        return {
            "extracted_entities": (
                result.entities if hasattr(result, "entities") else []
            ),
            "attribute": result,
        }


class EdgeExtractor(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    async def __call__(self, state):

        prompt_vars = {"transcripts": state.get("transcript", "")}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEntities)
        result = await llm.ainvoke(prompt)
        return {
            "extracted_entities": (
                result.entities if hasattr(result, "entities") else []
            ),
            "attribute": result,
        }


class GraphWriter(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    async def __call__(self, state):

        prompt_vars = {"transcripts": state.get("transcript", "")}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEntities)
        result = await llm.ainvoke(prompt)
        return {
            "extracted_entities": (
                result.entities if hasattr(result, "entities") else []
            ),
            "attribute": result,
        }
