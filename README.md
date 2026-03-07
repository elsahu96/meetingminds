# MeetingMind 🧠

> Agentic Meeting Intelligence with Temporal Knowledge Graph  
> LangChain × SurrealDB Hackathon

## Project Structure

```
meetingmind/
├── frontend/          # React + TypeScript + Vite + Tailwind CSS + D3
└── backend/           # FastAPI + LangGraph + SurrealDB (skeleton)
```

## Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
uvicorn app.main:app --reload
# → http://localhost:8000
```

## Stack

| Layer     | Tech                                      |
|-----------|-------------------------------------------|
| Frontend  | React 18, TypeScript, Vite, Tailwind CSS, D3 v7 |
| Backend   | FastAPI, LangGraph, LangChain, SurrealDB  |
| AI        | Anthropic Claude (claude-3-5-sonnet)      |
| Memory    | SurrealDB (graph + vector + document)     |
| Tracing   | LangSmith                                 |
