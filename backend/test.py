"""
Call the local /process-notes API with a mock request.

Requires the API server to be running: uvicorn app.main:app --reload --port 8000
"""

import asyncio
from pathlib import Path

import httpx

# Path to meeting notes (project root is backend/..)
NOTES_FILE = Path(__file__).resolve().parent.parent / "testing" / "meeting_notes" / "notes_01.txt"


async def main():
    notes = NOTES_FILE.read_text().strip()
    url = "http://localhost:8000/process-notes"
    payload = {
        "notes": notes
    }

    print(f"POST {url}")
    print(f"Notes from: {NOTES_FILE}")
    print(f"Notes length: {len(notes)} chars")
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            print("Status:", resp.status_code)
            print()
            # Transcript
            if "transcript" in data and data["transcript"]:
                print("--- transcript ---")
                print(data["transcript"])
                print()
            # Extracted entities
            if "extracted_entities" in data and data["extracted_entities"]:
                print("--- extracted_entities ---")
                for i, e in enumerate(data["extracted_entities"], 1):
                    print(f"{i}. [{e.get('type', '?')}] {e.get('name', '')}")
                    print(f"   {e.get('description', '')}")
                    print()
            # Any other keys
            for k in data:
                if k in ("transcript", "extracted_entities"):
                    continue
                if data[k] is not None:
                    print(f"--- {k} ---")
                    print(data[k])
                    print()
        except httpx.ConnectError:
            print("Error: Could not connect to localhost:8000. Is the API server running?")
            print("Start it with: cd backend && uvicorn app.main:app --reload --port 8000")
        except httpx.HTTPStatusError as e:
            print("Error:", e.response.status_code, e.response.text)


if __name__ == "__main__":
    asyncio.run(main())
