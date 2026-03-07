from fastapi import APIRouter

from app.core.schemas import IngestRequest
from app.graph.flow import ProcessNotes

router = APIRouter()


@router.post("/process-notes", response_model=dict)
async def process_notes(req: IngestRequest) -> dict:
    processor = ProcessNotes()
    payload = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    payload["mode"] = payload.get("mode") or "ingest"
    return await processor(payload)
