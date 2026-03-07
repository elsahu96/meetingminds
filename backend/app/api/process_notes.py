from fastapi import APIRouter

from app.graph.flow import ProcessNotes
from app.graph.state import NotesRequest
from app.graph.nodes import GraphWriter
from app.db.client import SurrealDBClient
from typing import List, Dict, Any


router = APIRouter()


@router.post("/process-notes", response_model=dict)
async def process_notes(req: NotesRequest) -> dict:
    processor = ProcessNotes()
    return await processor(req)


@router.post("/write-graph", response_model=dict)
async def write_graph(req: NotesRequest) -> dict:
    writer = GraphWriter()
    return await writer(req)


@router.get("/graph")
async def get_graph() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch the full knowledge graph from SurrealDB."""
    client = SurrealDBClient()
    await client.connect()

    # Fetch all nodes from different tables
    nodes = []

    # Fetch persons
    persons = await client.get_nodes("person")
    for person in persons:
        nodes.append({
            "id": person.get("id", "").split(":")[-1],  # Extract ID after colon
            "type": "person",
            "label": person.get("name", "").lower().replace(" ", "_"),
            "tooltip": {
                "type": "PERSON",
                "name": person.get("name", ""),
                "role": person.get("role", ""),
                "commits": f"{person.get('commit_count', 0)} open",
                "risk": f"{person.get('risk_score', 0)}/5"
            }
        })

    # Fetch actions
    actions = await client.get_nodes("action")
    for action in actions:
        nodes.append({
            "id": action.get("id", "").split(":")[-1],
            "type": "action",
            "label": action.get("description", "").lower().replace(" ", "-")[:20],
            "overdue": action.get("status") == "overdue",
            "tooltip": {
                "type": "ACTION",
                "name": action.get("description", ""),
                "role": f"{action.get('assignee', 'Unknown')} · {action.get('status', 'pending')}",
                "commits": action.get("status", "pending").upper(),
                "risk": action.get("priority", "low")
            }
        })

    # Fetch meetings
    meetings = await client.get_nodes("meeting")
    for meeting in meetings:
        nodes.append({
            "id": meeting.get("id", "").split(":")[-1],
            "type": "meeting",
            "label": meeting.get("title", "").lower().replace(" ", "-"),
            "tooltip": {
                "type": "MEETING",
                "name": meeting.get("title", ""),
                "role": meeting.get("date", ""),
                "commits": f"{meeting.get('action_count', 0)} actions",
                "risk": "—"
            }
        })

    # Fetch topics
    topics = await client.get_nodes("topic")
    for topic in topics:
        nodes.append({
            "id": topic.get("id", "").split(":")[-1],
            "type": "topic",
            "label": topic.get("name", "").lower().replace(" ", "-"),
            "tooltip": {
                "type": "TOPIC",
                "name": topic.get("name", ""),
                "role": topic.get("category", ""),
                "commits": f"importance:{topic.get('importance', 0):.2f}",
                "risk": "—"
            }
        })

    # Fetch edges
    edges = []
    relationships = await client.get_edges("assigned_to")
    for rel in relationships:
        edges.append({
            "source": rel.get("in", "").split(":")[-1],
            "target": rel.get("out", "").split(":")[-1],
            "type": "committed"
        })

    originated_rels = await client.get_edges("originated_from")
    for rel in originated_rels:
        edges.append({
            "source": rel.get("in", "").split(":")[-1],
            "target": rel.get("out", "").split(":")[-1],
            "type": "originated"
        })

    return {"nodes": nodes, "edges": edges}
