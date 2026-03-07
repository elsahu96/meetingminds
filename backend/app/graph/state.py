"""
MeetingMind LangGraph state.

TODO: wire up nodes in flow.py
"""

from __future__ import annotations
from typing import TypedDict, Optional

from pydantic import BaseModel


class NotesRequest(BaseModel):
    notes: str
    nodes: list = None
    edges: list = None


class MeetingMindState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────────────────────
    transcript: str  # raw transcript text
    meeting_title: str
    meeting_date: str
    query: Optional[str]  # user question (query mode only)
    mode: str  # "ingest" | "query"

    # ── Ingestion ──────────────────────────────────────────────────────────
    meeting_id: str  # SurrealDB record id
    speakers: list[str]
    segments: list[dict]  # [{speaker, text, timestamp}]

    # ── Extraction ─────────────────────────────────────────────────────────
    extracted_entities: dict  # {people, decisions, actions, blockers, topics}
    extraction_confidence: float
    extraction_attempts: int

    # ── Graph ──────────────────────────────────────────────────────────────
    graph_writes: list[dict]  # records written to SurrealDB

    # ── Delta ──────────────────────────────────────────────────────────────
    delta_report: dict  # {overdue, new_blockers, contradictions, at_risk}

    # ── Output ─────────────────────────────────────────────────────────────
    final_response: str
    error: Optional[str]
