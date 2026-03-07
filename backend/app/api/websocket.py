"""
WS /ws/graph-updates

Pushes live graph diffs to all connected clients after each ingest.

TODO: implement ConnectionManager and broadcast after graph writes.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# TODO: replace with a proper ConnectionManager that supports broadcasting
active_connections: list[WebSocket] = []


@router.websocket("/ws/graph-updates")
async def graph_updates(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection alive; updates are pushed from ingest handler
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_graph_update(payload: dict):
    """Call this from the ingest handler after writing to SurrealDB."""
    import json
    dead = []
    for ws in active_connections:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)
