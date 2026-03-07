"""
SurrealDB async client wrapper.

TODO: implement all methods using the surrealdb Python SDK.
"""

from __future__ import annotations
from app.core.config import get_settings
from surrealdb import AsyncSurreal
from datetime import datetime

settings = get_settings()


class SurrealDBClient:
    """Async wrapper around the SurrealDB Python SDK."""

    def __init__(self):
        # Don't connect here - connection is async
        self.db = None

    async def connect(self) -> None:
        self.db = AsyncSurreal(settings.surrealdb_url)
        await self.db.signin(
            {"username": settings.surrealdb_user, "password": settings.surrealdb_pass}
        )
        await self.db.use(settings.surrealdb_namespace, settings.surrealdb_database)
        await self.db.connect()

    async def query(self, surql: str, vars: dict | None = None) -> list:
        return await self.db.query(surql, vars or {})

    async def get_nodes(self, table: str, record_id: str | None = None) -> dict | list:
        """
        Get a node or all nodes from a table.

        Args:
            table: The table name
            record_id: Optional record ID to get a specific node

        Returns:
            dict if record_id is provided, list of dicts if not
        """
        if record_id is not None:
            node = f"{table}:{record_id}"
            return await self.db.select(node)
        res = await self.db.select(table)
        return res or []

    async def get_edges(
        self,
        rel_type: str,
        from_id: str | None = None,
        to_id: str | None = None,
    ) -> list:
        """
        Get edge or edges of a specific type, optionally filtered by from_id or to_id.

        Args:
            rel_type: The relationship type (edge table name)
            from_id: Optional source node ID to filter by
            to_id: Optional target node ID to filter by

        Returns:
            list of edge records
        """
        if from_id is None and to_id is None:
            return await self.db.query(f"SELECT * FROM {rel_type};")
        if from_id is not None and to_id is not None:
            return await self.db.query(
                f"SELECT * FROM {rel_type} WHERE in = $from_id AND out = $to_id;",
                {"from_id": from_id, "to_id": to_id},
            )
        if from_id is not None:
            return await self.db.query(
                f"SELECT * FROM {rel_type} WHERE in = $from_id;",
                {"from_id": from_id},
            )
        return await self.db.query(
            f"SELECT * FROM {rel_type} WHERE out = $to_id;",
            {"to_id": to_id},
        )

    async def create_node(
        self, table: str, data: dict, record_id: str | None = None
    ) -> dict:
        """
        Create a node in a table.

        Args:
            table: The table name
            data: The node data
            record_id: Optional record ID to use for the node

        Returns:
            The created node record
        """
        node = f"{table}:{record_id}" if record_id else table
        return await self.db.create(node, data)

    async def create_edge(
        self, from_id: str, rel_type: str, to_id: str, attrs: dict = None
    ) -> list:
        """
        Create an edge between two nodes.

        Args:
            from_id: Source node ID (e.g., "person:alice")
            rel_type: Relationship type (edge table name)
            to_id: Target node ID (e.g., "action:1")
            attrs: Optional attributes to store on the edge

        Returns:
            list of created edge records
        """
        query = f"RELATE {from_id} -> {rel_type} -> {to_id}"
        if attrs:
            query += " CONTENT $attrs"
            return await self.db.query(query, {"attrs": attrs})
        else:
            return await self.db.query(query)

    async def update_node(self, table: str, record_id: str, data: dict) -> list:
        """
        Update a node in a table.

        Args:
            table: The table name
            record_id: The record ID of the node to update
            data: The data to update the node with

        Returns:
            list of updated node records
        """
        node = f"{table}:{record_id}"
        query = f"UPDATE {node} MERGE $data RETURN AFTER"
        return await self.db.query(query, {"data": data})

    async def update_edge(
        self, from_id: str, rel_type: str, to_id: str, data: dict
    ) -> list:
        """
        Update an edge between two nodes.

        Args:
            from_id: Source node ID (e.g., "person:alice")
            rel_type: Relationship type (edge table name)
            to_id: Target node ID (e.g., "action:1")
            data: The data to update the edge with

        Returns:
            list of updated edge records
        """
        query = (
            f"UPDATE {rel_type} MERGE $data "
            "WHERE in = $from_id AND out = $to_id "
            "RETURN AFTER"
        )
        return await self.db.query(
            query,
            {"from_id": from_id, "to_id": to_id, "data": data},
        )

    async def delete_node(self, table: str, record_id: str) -> dict | None:
        """
        Delete a node from a table.

        Args:
            table: The table name
            record_id: The record ID of the node to delete

        Returns:
            The deleted node record
        """
        node = f"{table}:{record_id}"
        return await self.db.delete(node)

    async def delete_table(self, table: str, drop: bool = False) -> list:
        """
        Delete a table.

        Args:
            table: The table name
            drop: Whether to drop the table (remove all data and structure)

        Returns:
            list of deleted table records
        """
        if drop:
            return await self.db.query(f"REMOVE TABLE {table};")
        return await self.db.query(f"DELETE {table};")

    async def delete_edge(self, from_id: str, rel_type: str, to_id: str) -> list:
        """
        Delete an edge between two nodes.

        Args:
            from_id: Source node ID (e.g., "person:alice")
            rel_type: Relationship type (edge table name)
            to_id: Target node ID (e.g., "action:1")

        Returns:
            list of deleted edge records
        """
        query = f"""
        DELETE {rel_type}
        WHERE in = type::record($from_id)
          AND out = type::record($to_id)
        RETURN BEFORE;
        """
        return await self.db.query(query, {"from_id": from_id, "to_id": to_id})

    async def get_full_graph(self):
        # TODO: SELECT * FROM person, meeting, action, decision, blocker, topic
        # and all edge tables, return GraphDataResponse
        raise NotImplementedError


# Singleton
_client: SurrealDBClient | None = None


async def get_client() -> SurrealDBClient:
    global _client
    if _client is None:
        _client = SurrealDBClient()
        await _client.connect()
    return _client
