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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --env-file .env
```



## Stack

| Layer     | Tech                                      |
|-----------|-------------------------------------------|
| Frontend  | React 18, TypeScript, Vite, Tailwind CSS, D3 v7 |
| Backend   | FastAPI, LangGraph, LangChain, SurrealDB  |
| AI        | Anthropic Claude (claude-3-5-sonnet)      |
| Memory    | SurrealDB (graph + vector + document)     |
| Tracing   | LangSmith                                 |
