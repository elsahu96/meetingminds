"""
POST /ingest

Accepts a meeting transcript, runs the LangGraph ingestion pipeline,
and returns a summary + delta report.

TODO: wire up the LangGraph flow from app/graph/flow.py
"""
from fastapi import APIRouter
from app.core.schemas import IngestRequest, IngestResponse, DeltaReport

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_transcript(req: IngestRequest) -> IngestResponse:
    # TODO: run LangGraph ingest flow
    # from app.graph.flow import run_ingest
    # result = await run_ingest(req)
    # return result
    raise NotImplementedError("Ingest endpoint not yet implemented")
