# MeetingMind — Frontend

React 18 + TypeScript + Vite + Tailwind CSS + D3 v7

## Setup

```bash
npm install
npm run dev
# → http://localhost:5173
```

## Scripts

| Command           | Description                        |
|-------------------|------------------------------------|
| `npm run dev`     | Start Vite dev server (HMR)        |
| `npm run build`   | Type-check + production build      |
| `npm run preview` | Preview production build           |
| `npm run lint`    | ESLint                             |
| `npm run type-check` | TypeScript check without emit   |

## Structure

```
src/
├── main.tsx                  # React entry point
├── App.tsx                   # Root component, global state
├── index.css                 # Tailwind directives + custom components
│
├── types/
│   └── index.ts              # All TypeScript interfaces
│
├── lib/
│   ├── graphConfig.ts        # D3 node/edge visual styles + legend
│   ├── seedData.ts           # Demo data (nodes, edges, transcripts, chat)
│   └── api.ts                # Axios API client + WebSocket connector
│
├── hooks/
│   ├── useForceGraph.ts      # D3 force simulation + drag logic
│   └── useProcessing.ts      # Transcript processing state machine
│
└── components/
    ├── App.tsx               # Root layout
    ├── Topbar.tsx            # Header bar
    ├── StatusBar.tsx         # Footer stats bar
    ├── GraphToolbar.tsx      # Graph panel header + legend
    ├── ForceGraph.tsx        # D3 SVG force graph (drag, highlight, tooltip)
    ├── IngestPanel.tsx       # Transcript upload queue + delta report
    ├── TranscriptCard.tsx    # Individual transcript card
    └── ChatPanel.tsx         # Agent query chat interface
```

## Connecting to the Backend

The Vite dev server proxies `/api` → `http://localhost:8000` and
`/ws` → `ws://localhost:8000`. Start the backend and the frontend
will automatically route API calls through.

To use mock data without a backend, the app seeds itself from
`src/lib/seedData.ts` on load.
