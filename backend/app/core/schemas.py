from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ─── Graph ────────────────────────────────────────────────────────────────────

NodeType = Literal["person", "meeting", "action", "decision", "blocker", "topic"]
EdgeType = Literal["committed", "originated", "blocks", "contradicts"]


class NodeTooltip(BaseModel):
    type: str
    name: str
    role: str
    commits: str
    risk: str


class GraphNode(BaseModel):
    id: str
    type: NodeType
    label: str
    overdue: bool = False
    tooltip: NodeTooltip


class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType


class GraphDataResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ─── Ingest ───────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    transcript: str = Field(..., description="Raw meeting transcript text")
    meeting_title: str = Field(..., description="Human-readable meeting title")
    meeting_date: str  = Field(..., description="ISO date string YYYY-MM-DD")


class OverdueItem(BaseModel):
    person: str
    action: str
    deadline: str
    days_overdue: int
    meeting_origin: str


class ContradictionItem(BaseModel):
    decision_new: str
    decision_old: str
    meeting_new: str
    meeting_old: str
    severity: Literal["low", "medium", "high"]


class BlockerItem(BaseModel):
    description: str
    affects_count: int
    severity: Literal["low", "medium", "high"]


class AtRiskItem(BaseModel):
    person: str
    open_commitments: int
    blocking_count: int
    risk_score: float


class DeltaReport(BaseModel):
    overdue: list[OverdueItem] = []
    contradictions: list[ContradictionItem] = []
    blockers: list[BlockerItem] = []
    at_risk: list[AtRiskItem] = []


class IngestResponse(BaseModel):
    meeting_id: str
    summary: str
    entities_extracted: int
    delta_report: DeltaReport


# ─── Query ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about meeting history")
    thread_id: Optional[str] = Field(None, description="Session thread ID for continuity")


class ApiCitation(BaseModel):
    meeting_title: str
    date: str
    entity_type: str
    entity_id: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[ApiCitation] = []


# ─── WebSocket ────────────────────────────────────────────────────────────────

class WebSocketGraphUpdate(BaseModel):
    type: Literal["graph_update"] = "graph_update"
    new_nodes: list[GraphNode] = []
    new_edges: list[GraphEdge] = []
