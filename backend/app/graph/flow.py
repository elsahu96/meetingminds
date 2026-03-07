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

from app.graph.state import NotesRequest, QueryRequest
from langsmith import traceable
from langgraph.graph import END, StateGraph, START
from app.graph.nodes import (
    EdgeExtractor,
    GraphWriter,
    NodeExtrator,
    AgenticSearch,
    InferAnswer,
    SurrealQueryExecutor
)


# ─── Graph assembly ───────────────────────────────────────────────────────────


@traceable
class ProcessNotes:
    @traceable
    def __init__(self):
        builder = StateGraph(NotesRequest)
        builder.add_node("node_extractor", NodeExtrator())
        builder.add_node("edge_extractor", EdgeExtractor())
        builder.add_node("graph_writer", GraphWriter())

        builder.add_edge(START, "node_extractor")
        builder.add_edge("node_extractor", "edge_extractor")
        builder.add_edge("edge_extractor", "graph_writer")
        builder.add_edge("graph_writer", END)
        self.graph = builder.compile()

    @traceable
    async def __call__(self, request):
        initial_state = {"notes": request.notes}
        output = await self.graph.ainvoke(initial_state)
        return output

class Query:

    @traceable
    def __init__(self):
        def route_start(state: QueryRequest):
            if state.surreal_query:
                return "surreal_query_executor"
            if state.question:
                return "agentic_search"
            return END

        builder = StateGraph(QueryRequest)
        builder.add_node("agentic_search", AgenticSearch())
        builder.add_node("surreal_query_executor", SurrealQueryExecutor())
        builder.add_node("answer_inferral", InferAnswer())

        builder.add_conditional_edges(START, route_start)
        builder.add_edge("agentic_search", "surreal_query_executor")
        builder.add_edge("surreal_query_executor", "answer_inferral")
        builder.add_edge("answer_inferral", END)
        self.graph = builder.compile()

    @traceable
    async def __call__(self, request):
        initial_state = {
            "question": getattr(request, "question", None),
            "surreal_query": getattr(request, "surreal_query", None),
        }
        output = await self.graph.ainvoke(initial_state)
        return output
