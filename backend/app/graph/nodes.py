from app.graph.base import BaseAgent
from pydantic import BaseModel, Field
from app.graph.state import NotesRequest
from app.db.client import SurrealDBClient

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExtractedEntity(BaseModel):
    type: str = Field(description="One of: Person, Team, Topic, Action")
    name: str = Field(description="Canonical name for the entity")
    description: str = Field(description="1-3 sentence summary")


class ExtractedEntities(BaseModel):
    """JSON array of extracted entities from a meeting transcript."""

    entities: list[ExtractedEntity] = Field(
        default_factory=list, description="List of extracted entities"
    )

class ExtractedEdge(BaseModel):
    from_id: str = Field(description="Source node ID in format 'Type:Name'")
    rel_type: str = Field(description="Relationship type")
    to_id: str = Field(description="Target node ID in format 'Type:Name'")


class ExtractedEdges(BaseModel):
    """JSON array of extracted edges from nodes."""

    edges: list[ExtractedEdge] = Field(
        default_factory=list, description="List of extracted edges"
    )


class NodeExtrator(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_01"

    async def __call__(self, state: NotesRequest):
        prompt_vars = {"transcripts": state.notes}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEntities)
        result = await llm.ainvoke(prompt)
        return {
            "nodes": (
                result.entities if hasattr(result, "entities") else []
            )
        }


class EdgeExtractor(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_02"

    async def __call__(self, state: NotesRequest):

        prompt_vars = {"nodes": state.nodes}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEdges)
        result = await llm.ainvoke(prompt)
        return {
            "edges": (
                result.edges if hasattr(result, "edges") else []
            )
        }


class GraphWriter:

    def __init__(self):
        self.db = SurrealDBClient()

    async def __call__(self, state: NotesRequest):

        if self.db.db is None:
            await self.db.connect()

        logger.info("Creating nodes")
        for node in state.nodes:
            logger.info(f"Processing node: {node}")
            record = await self.db.create_node(
                table=node["type"].lower(),
                record_id=node["name"].lower().replace(" ", "_").replace("-",""),
                data=node
            )
            logger.info(f"Recorded node: {record}")

        for edge in state.edges:
            logger.info(f"Processing edge: {edge}")
            record = await self.db.create_edge(
                from_id=edge["from_id"].lower().replace(" ", "_").replace("-",""),
                rel_type=edge["rel_type"],
                to_id=edge["to_id"].lower().replace(" ", "_").replace("-",""),
            )
            logger.info(f"Recorded edge: {record}")

        return {"status": "success"}


