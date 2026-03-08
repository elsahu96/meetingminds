from fastapi import APIRouter
from app.db.client import SurrealDBClient
from app.core.schemas import GraphDataResponse, GraphNode, GraphEdge
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/graph", response_model=GraphDataResponse)
async def get_graph():
    try:
        client = SurrealDBClient()
        await client.connect()

        nodes = []
        edges = []

        # Get all nodes from different tables
        node_tables = ["person", "action",  "topic", "team"]
        for table in node_tables:
            table_nodes = await client.get_nodes(table)
            logger.info("table_nodes type: %s", type(table_nodes))

            if not isinstance(table_nodes, list):
                logger.warning("Unexpected nodes payload for %s: %r", table, table_nodes)
                continue

            for n in table_nodes:
                if not isinstance(n, dict):
                    continue
                node_type = table
                if table == "person":
                    tooltip = {
                        "type": "Person",
                        "name": n.get("name", ""),
                        "role": n.get("role", ""),
                        "commits": "",  # TODO
                        "risk": ""  # TODO
                    }
                elif table == "action":
                    tooltip = {
                        "type": "Action",
                        "name": n.get("name", n.get("description", "")),
                        "role": "",
                        "commits": "",
                        "risk": ""
                    }
                elif table == "topic":
                    tooltip = {
                        "type": "Topic",
                        "name": n.get("name", n.get("description", "")),
                        "role": "",
                        "commits": "",
                        "risk": ""
                    }
                elif table == "team":
                    tooltip = {
                        "type": "Team",
                        "name": n.get("name", n.get("description", "")),
                        "role": "",
                        "commits": "",
                        "risk": ""
                    }
                else:
                    tooltip = {
                        "type": table.capitalize(),
                        "name": n.get("name", n.get("description", "")),
                        "role": "",
                        "commits": "",
                        "risk": ""
                    }
                
                nodes.append(GraphNode(
                    id=str(n["id"]),
                    type=node_type,
                    label=n.get("name", n.get("title", n.get("description", ""))),
                    overdue=n.get("status") == "pending" and n.get("deadline", "") < "now()" if table == "action" else False,
                    tooltip=tooltip
                ))

        # Get all edges from different relations
        edge_types = ["assigned_to", "blocked_by", "helps_to_achieve", "reports_to", "work_for"]
        for rel_type in edge_types:
            table_edges = await client.get_edges(rel_type)
            logger.info("table_edges type: %s", type(table_edges))

            if not isinstance(table_edges, list):
                logger.warning("Unexpected edges payload for %s: %r", rel_type, table_edges)
                continue

            for e in table_edges:
                if not isinstance(e, dict):
                    continue
                if "in" not in e or "out" not in e:
                    continue
                edges.append(GraphEdge(
                    source=str(e["in"]),
                    target=str(e["out"]),
                    type=rel_type
                ))

        return GraphDataResponse(nodes=nodes, edges=edges)

    except Exception as e:
        logger.exception("Failed to get graph: %s", e)
        raise

