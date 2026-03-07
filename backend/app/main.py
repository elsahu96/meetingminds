from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.process_notes import router as process_nodes
from app.api.query import router as query

settings = get_settings()

app = FastAPI(
    title="MeetingMind API",
    description="Agentic Meeting Intelligence with Temporal Knowledge Graph",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_nodes, tags=["process"])
app.include_router(query, tags=["query"])


@app.get("/health")
async def health():
    return {"status": "ok"}
