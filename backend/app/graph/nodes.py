from app.graph.base import BaseAgent
from pydantic import BaseModel, Field
from app.graph.state import NotesRequest, QueryRequest
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
        entities = result.entities if hasattr(result, "entities") else []
        return {"extracted_entities": [e.model_dump() if hasattr(e, "model_dump") else e for e in entities]}


class EdgeExtractor(BaseAgent):

    model_name = "gpt-4o-mini"
    prompt_name = "prompt_02"

    async def __call__(self, state: NotesRequest):

        prompt_vars = {"nodes": state.nodes}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(ExtractedEdges)
        result = await llm.ainvoke(prompt)
        return {"edges": (result.edges if hasattr(result, "edges") else [])}


class GraphWriter:

    def __init__(self):
        self.db = SurrealDBClient()

    async def __call__(self, state: NotesRequest):

        if self.db.db is None:
            await self.db.connect()

        def _as_dict(obj):
            if isinstance(obj, dict):
                return obj
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if hasattr(obj, "dict"):
                return obj.dict()
            raise TypeError(f"Unsupported node/edge type: {type(obj)!r}")

        logger.info("Creating nodes")
        for node in (state.nodes or []):
            node_data = _as_dict(node)
            logger.info(f"Processing node: {node_data}")
            record = await self.db.create_node(
                table=node_data["type"].lower(),
                record_id=node_data["name"].lower().replace(" ", "_").replace("-", ""),
                data=node_data
            )
            logger.info(f"Recorded node: {record}")

        for edge in (state.edges or []):
            edge_data = _as_dict(edge)
            logger.info(f"Processing edge: {edge_data}")
            record = await self.db.create_edge(
                from_id=edge_data["from_id"].lower().replace(" ", "_").replace("-", ""),
                rel_type=edge_data["rel_type"],
                to_id=edge_data["to_id"].lower().replace(" ", "_").replace("-", ""),
            )
            logger.info(f"Recorded edge: {record}")

        return {"status": "Nodes and edges recorded successfully"}


class AgenticSearch(BaseModel):
    model_name = "gpt-4o-mini"
    prompt_name = "prompt_03"

    async def __call__(self, state: QueryRequest):

        pass
