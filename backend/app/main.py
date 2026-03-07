from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import ingest, query, graph, websocket

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

app.include_router(ingest.router,    tags=["ingest"])
app.include_router(query.router,     tags=["query"])
app.include_router(graph.router,     tags=["graph"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/health")
async def health():
    return {"status": "ok"}
