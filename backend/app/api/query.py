"""
POST /query

Accepts a natural language question, runs the LangGraph query flow,
and returns a cited answer.

TODO: wire up the LangGraph query flow from app/graph/flow.py
"""
from fastapi import APIRouter
from app.graph.flow import Query as QueryFlow
from app.graph.state import QueryRequest

router = APIRouter()

@router.post("/query", response_model=dict)
async def query_agent(req: QueryRequest) -> dict:
    flow = QueryFlow()
    return await flow(req)
