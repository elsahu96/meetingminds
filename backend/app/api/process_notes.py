from fastapi import APIRouter

from app.graph.flow import ProcessNotes
from app.graph.state import NotesRequest
from app.graph.nodes import GraphWriter


router = APIRouter()



@router.post("/process-notes", response_model=dict)
async def process_notes(req: NotesRequest) -> dict:
    processor = ProcessNotes()
    return await processor(req)


@router.post("/write-graph", response_model=dict)
async def write_graph(req: NotesRequest) -> dict:
    writer = GraphWriter()
    return await writer(req)
