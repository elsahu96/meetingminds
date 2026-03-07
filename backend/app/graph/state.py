"""
MeetingMind LangGraph state.

TODO: wire up nodes in flow.py
"""

from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class NotesRequest(BaseModel):
    notes: str
    nodes: list = []
    edges: list = []
    status: str = ""

class QueryRequest(BaseModel):
    question: str
    graph_information: list = None
    response: str = None

