# MeetingMind — Backend

FastAPI + LangGraph + SurrealDB skeleton.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
```

## Run

```bash
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

## Structure

```
app/
├── main.py              # FastAPI app + CORS + router registration
├── core/
│   ├── config.py        # Pydantic settings (reads .env)
│   └── schemas.py       # All request/response Pydantic models
├── api/
│   ├── ingest.py        # POST /ingest
│   ├── query.py         # POST /query
│   ├── graph.py         # GET /graph, /commitments/overdue, /risk/...
│   └── websocket.py     # WS /ws/graph-updates
├── db/
│   ├── client.py        # Async SurrealDB client wrapper
│   └── queries.py       # Named SurrealQL query strings
└── graph/
    ├── state.py         # MeetingMindState TypedDict
    └── flow.py          # LangGraph 5-node flow (stubs)
```

## Implementation Order

1. `app/db/client.py` — connect to SurrealDB, implement upsert methods
2. `app/graph/flow.py` — implement node functions one by one
3. `app/api/ingest.py` — wire `run_ingest` from flow.py
4. `app/api/query.py`  — wire `run_query` from flow.py
5. `app/api/graph.py`  — wire SurrealDB queries
6. `app/api/websocket.py` — broadcast after graph writes

## API Endpoints

| Method | Path                            | Description                    |
|--------|---------------------------------|--------------------------------|
| POST   | /ingest                         | Ingest meeting transcript      |
| POST   | /query                          | Query the agent                |
| GET    | /graph                          | Full knowledge graph           |
| GET    | /commitments/overdue            | Overdue action items           |
| GET    | /risk/single-point-of-failure   | At-risk people analysis        |
| WS     | /ws/graph-updates               | Live graph diffs               |
| GET    | /health                         | Health check                   |
| GET    | /docs                           | Swagger UI                     |
