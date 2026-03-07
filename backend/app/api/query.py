"""
POST /query

Accepts a natural language question, runs the LangGraph query flow,
and returns a cited answer.

TODO: wire up the LangGraph query flow from app/graph/flow.py
"""
from fastapi import APIRouter
from app.core.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_agent(req: QueryRequest) -> QueryResponse:
    # TODO: run LangGraph query flow
    # from app.graph.flow import run_query
    # result = await run_query(req)
    # return result
    raise NotImplementedError("Query endpoint not yet implemented")
