"""
Test script for SurrealDB connection.

This script tests the basic connection and operations with SurrealDB.
It connects to the remote SurrealDB server configured in app/core/config.py.

Make sure your SurrealDB server is running and accessible before running this script.
"""

import asyncio
from app.db.client import SurrealDBClient


async def test_connection():
    """Test basic SurrealDB connection and operations."""
    print("Testing SurrealDB connection...")

    from app.core.config import get_settings
    settings = get_settings()
    print(f"Connecting to SurrealDB at {settings.surrealdb_url}...")

    client = SurrealDBClient()

    try:
        # Connect to database
        await client.connect()
        print("✓ Connected to SurrealDB")

        # Test creating a table and inserting data
        print("\nTesting data operations...")

        # Create a test person
        person_data = {
            "name": "Alice Johnson",
            "role": "Product Manager",
            "email": "alice@company.com"
        }

        result = await client.create_node("person", person_data, "alice")
        print(f"✓ Created person: {result}")

        # Create a test action
        action_data = {
            "description": "Schedule follow-up meeting",
            "status": "pending",
            "priority": "high",
            "created_at": "2024-01-15T10:00:00Z"
        }

        result = await client.create_node("action", action_data, "1")
        print(f"✓ Created action: {result}")

        # Create a relationship between them
        result = await client.create_edge("person:alice", "assigned_to", "action:1")
        print(f"✓ Created relationship: {result}")

        # Query all persons
        persons = await client.get_nodes("person")
        print(f"✓ Retrieved persons: {len(persons)} records")

        # Query all actions
        actions = await client.get_nodes("action")
        print(f"✓ Retrieved actions: {len(actions)} records")

        # Query relationships
        edges = await client.get_edges("assigned_to")
        print(f"✓ Retrieved relationships: {len(edges)} records")

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("Make sure SurrealDB is running and accessible.")
        return False

    return True


async def main():
    """Main test function."""
    print("SurrealDB Connection Test")
    print("=" * 40)

    success = await test_connection()

    if success:
        print("\n🎉 SurrealDB is working correctly!")
    else:
        print("\n Nope")

if __name__ == "__main__":
    asyncio.run(main())