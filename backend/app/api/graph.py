"""
GET /graph                       → full knowledge graph for rendering
GET /commitments/overdue         → overdue action items
GET /risk/single-point-of-failure → people with highest accountability risk

TODO: wire up SurrealDB queries from app/db/queries.py
"""
from fastapi import APIRouter
from app.core.schemas import GraphDataResponse, AtRiskItem, OverdueItem

router = APIRouter()


@router.get("/graph", response_model=GraphDataResponse)
async def get_graph() -> GraphDataResponse:
    # TODO: fetch from SurrealDB
    # from app.db.client import get_client
    # client = await get_client()
    # return await client.get_full_graph()
    raise NotImplementedError("Graph endpoint not yet implemented")


@router.get("/commitments/overdue", response_model=list[OverdueItem])
async def get_overdue() -> list[OverdueItem]:
    # TODO: run QUERY_OVERDUE_COMMITMENTS against SurrealDB
    raise NotImplementedError("Overdue endpoint not yet implemented")


@router.get("/risk/single-point-of-failure", response_model=list[AtRiskItem])
async def get_risk() -> list[AtRiskItem]:
    # TODO: run QUERY_SINGLE_POINT_OF_FAILURE against SurrealDB
    raise NotImplementedError("Risk endpoint not yet implemented")
