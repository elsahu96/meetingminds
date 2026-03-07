from fastapi import APIRouter

from app.graph.flow import ProcessNotes
from app.graph.state import NotesRequest


router = APIRouter()


@router.post("/process-notes", response_model=dict)
async def process_notes(req: NotesRequest) -> dict:
    processor = ProcessNotes()
    return await processor(req)
