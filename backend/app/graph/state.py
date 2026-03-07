"""
MeetingMind LangGraph state.

TODO: wire up nodes in flow.py
"""

from __future__ import annotations
from pydantic import BaseModel


class NotesRequest(BaseModel):
    notes: str
    nodes: list = None
    edges: list = None
