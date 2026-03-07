"""
MeetingMind LangGraph 5-node flow.

Nodes:
  1. transcript_ingestor   – split transcript, detect speakers, create meeting record
  2. entity_extractor      – LLM extraction with retry on low confidence
  3. graph_writer          – upsert nodes/edges into SurrealDB, detect contradictions
  4. delta_detector        – diff new state vs previous snapshot
  5. response_synthesiser  – natural language answer with graph citations

TODO: implement each node function and wire into StateGraph.
"""
from app.graph.state import MeetingMindState
from langgraph.graph import END, StateGraph, START
from app.graph.nodes import EdgeExtractor, GraphWriter, NodeExtrator


# ─── Graph assembly ───────────────────────────────────────────────────────────

class ProcessNotes:
    def __init__(self):
        builder = StateGraph(MeetingMindState)
        builder.add_node("node_extractor", NodeExtrator())
        builder.add_node("edge_extractor", EdgeExtractor())
        builder.add_node("graph_writer", GraphWriter())

        builder.add_edge(START, "node_extractor")
        builder.add_edge("node_extractor", "edge_extractor")
        builder.add_edge("edge_extractor", "graph_writer")
        builder.add_edge("graph_writer", END)
        self.graph = builder.compile()

    async def __call__(self, request):
        output = await self.graph.ainvoke(request)
        return output
        
