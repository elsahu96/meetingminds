from fastapi import APIRouter
from app.db.client import SurrealDBClient
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_stats() -> dict:
    try:
        client = SurrealDBClient()
        await client.connect()

        counts: dict[str, int] = {}
        for table in ["person", "team", "action", "topic"]:
            rows = await client.get_nodes(table)
            counts[table] = len(rows) if isinstance(rows, list) else 0

        blocker_edges = await client.get_edges("blocked_by")
        counts["blocker"] = len(blocker_edges) if isinstance(blocker_edges, list) else 0

        return counts
    except Exception as e:
        logger.exception("Failed to get stats: %s", e)
        return {"person": 0, "team": 0, "action": 0, "topic": 0, "blocker": 0}
