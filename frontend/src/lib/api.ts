import axios from 'axios'
import type {
  IngestRequest, IngestResponse,
  QueryRequest, QueryResponse,
  GraphDataResponse,
} from '@/types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const apiClient = {
  /** Ingest a meeting transcript into the knowledge graph */
  ingest: (req: IngestRequest) =>
    api.post<IngestResponse>('/ingest', req).then(r => r.data),

  /** Query the agent with a natural language question */
  query: (req: QueryRequest) =>
    api.post<QueryResponse>('/query', req).then(r => r.data),

  /** Fetch the full knowledge graph for rendering */
  getGraph: () =>
    api.get<GraphDataResponse>('/graph').then(r => r.data),

  /** Get overdue commitments */
  getOverdue: () =>
    api.get('/commitments/overdue').then(r => r.data),

  /** Get single-point-of-failure analysis */
  getRisk: () =>
    api.get('/risk/single-point-of-failure').then(r => r.data),

  /** Process notes through the LangGraph pipeline */
  processNotes: (req: { notes: string; nodes?: unknown[]; edges?: unknown[]; status?: string }) => {
    console.log('[processNotes] req:', req)
    return api.post<{ notes?: string; nodes?: unknown[]; edges?: unknown[]; status?: string }>('/process-notes', req).then(r => r.data)
  },
}

/** WebSocket connection for live graph updates */
export function connectGraphWebSocket(
  onUpdate: (data: unknown) => void,
  onError?: (e: Event) => void,
): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/graph-updates`)
  ws.onmessage = (e) => {
    try {
      onUpdate(JSON.parse(e.data))
    } catch {
      console.warn('WS parse error', e.data)
    }
  }
  ws.onerror = onError ?? ((e) => console.error('WS error', e))
  return ws
}
