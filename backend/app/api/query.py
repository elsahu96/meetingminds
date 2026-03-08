"""
POST /query

Accepts a natural language question, runs the LangGraph query flow,
and returns a cited answer.

TODO: wire up the LangGraph query flow from app/graph/flow.py
"""
from fastapi import APIRouter
from app.graph.flow import Query as QueryFlow
from app.graph.state import QueryRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=dict)
async def query_agent(req: QueryRequest) -> dict:
    try:
        flow = QueryFlow()
        output = await flow(req)
        answer = output.get("response") or ""
        logger.info("query_agent completed successfully, answer length=%d", len(answer))
        return {"answer": answer, "citations": []}
    except Exception as e:
        logger.exception("query_agent failed: %s", e)
        raise
