from fastapi import APIRouter

from app.graph.flow import ProcessNotes
from app.graph.state import NotesRequest
from app.graph.nodes import GraphWriter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process-notes", response_model=dict)
async def process_notes(req: NotesRequest) -> dict:
    try:
        logger.info("process_notes started")
        logger.info(f"Request: {req}")
        processor = ProcessNotes()
        result = await processor(req)
        logger.info(
            "process_notes completed successfully: %s", result.get("status", "ok")
        )
        return result
    except Exception as e:
        logger.exception("process_notes failed: %s", e)
        raise


@router.post("/write-graph", response_model=dict)
async def write_graph(req: NotesRequest) -> dict:
    writer = GraphWriter()
    return await writer(req)
