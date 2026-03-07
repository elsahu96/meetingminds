"""
MeetingMind LangGraph 5-node flow.

Nodes:
  1. transcript_ingestor   - split transcript, detect speakers, create meeting record
  2. entity_extractor      - LLM extraction with retry on low confidence
  3. graph_writer          - upsert nodes/edges into SurrealDB, detect contradictions
  4. delta_detector        - diff new state vs previous snapshot
  5. response_synthesiser - natural language answer with graph citations

TODO: implement each node function and wire into StateGraph.
"""

from langchain_core.runnables import RunnableConfig
from app.graph.state import NotesRequest, QueryRequest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from app.graph.nodes import NodeExtrator, EdgeExtractor, GraphWriter
import logging

logger = logging.getLogger(__name__)


# ─── Graph assembly ───────────────────────────────────────────────────────────


class ProcessNotes:

    def __init__(self):
        builder = StateGraph(NotesRequest)
        builder.add_node("node_extractor", NodeExtrator())
        builder.add_node("edge_extractor", EdgeExtractor())
        builder.add_node("graph_writer", GraphWriter())

        builder.add_edge(START, "node_extractor")
        builder.add_edge("node_extractor", "edge_extractor")
        builder.add_edge("edge_extractor", "graph_writer")
        builder.add_edge("graph_writer", END)
        checkpointer = MemorySaver()
        self.graph = builder.compile(checkpointer=checkpointer)

    async def __call__(self, request):
        initial_state = {"notes": request.notes, "nodes": [], "edges": [], "status": ""}
        config: RunnableConfig = {"configurable": {"thread_id": "1"}}

        output = await self.graph.ainvoke(initial_state, config)

        state = self.graph.get_state(config)
        state_history = list(self.graph.get_state_history(config))
        logger.info(f"State: {state}")
        # print state_history
        logger.info(f"State history {state_history[0]}")

        return output


# class Query:
#     def __init__(self):
#         builder = StateGraph(QueryRequest)
#         builder.add_node("agentic_search", AgenticSearch())
#         builder.add_node("answer_inferral", InferAnswer())

#         builder.add_edge(START, "node_extractor")
#         builder.add_edge("node_extractor", "edge_extractor")
#         builder.add_edge("edge_extractor", "graph_writer")
#         builder.add_edge("graph_writer", END)
#         self.graph = builder.compile()

#     async def __call__(self, request):
#         initial_state = {"notes": request.notes}
#         output = await self.graph.ainvoke(initial_state)
#         return output
