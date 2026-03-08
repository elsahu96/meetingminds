// ─── Graph ────────────────────────────────────────────────────────────────────

export type NodeType = 'person' | 'meeting' | 'action' | 'decision' | 'blocker' | 'topic'
export type EdgeType = 'committed' | 'originated' | 'blocks' | 'contradicts'

export interface NodeTooltip {
  type: string
  name: string
  role: string
  commits: string
  risk: string
}

export interface GraphNode {
  id: string
  type: NodeType
  label: string
  overdue?: boolean
  tooltip: NodeTooltip
  // D3 simulation fields (mutated by D3)
  x?: number
  y?: number
  vx?: number
  vy?: number
  fx?: number | null
  fy?: number | null
}

export interface GraphEdge {
  source: string | GraphNode
  target: string | GraphNode
  type: EdgeType
}

// ─── Transcript ───────────────────────────────────────────────────────────────

export type TranscriptStatus = 'ready' | 'queued' | 'processing' | 'done'

export interface Transcript {
  id: string
  title: string
  date: string
  text: string
  status: TranscriptStatus
  progress: number
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface Citation {
  label: string
  nodeId?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'agent'
  text: string          // may contain safe HTML spans
  citations?: Citation[]
  timestamp: Date
}

// ─── Processing ───────────────────────────────────────────────────────────────

export type StepClass = 'done' | 'active' | 'warn'

export interface ExtractStep {
  id: string
  cls: StepClass
  icon: string
  text: string
  tag?: string
}

// ─── API ──────────────────────────────────────────────────────────────────────

export interface IngestRequest {
  transcript: string
  meeting_title: string
  meeting_date: string
}

export interface IngestResponse {
  meeting_id: string
  summary: string
  entities_extracted: number
  delta_report: DeltaReport
}

export interface QueryRequest {
  question: string
  thread_id?: string
}

export interface QueryResponse {
  answer: string
  citations: ApiCitation[]
}

export interface ApiCitation {
  meeting_title: string
  date: string
  entity_type: string
  entity_id: string
}

export interface DeltaReport {
  overdue: OverdueItem[]
  contradictions: ContradictionItem[]
  blockers: BlockerItem[]
  at_risk: AtRiskItem[]
}

export interface OverdueItem {
  person: string
  action: string
  deadline: string
  days_overdue: number
  meeting_origin: string
}

export interface ContradictionItem {
  decision_new: string
  decision_old: string
  meeting_new: string
  meeting_old: string
  severity: 'low' | 'medium' | 'high'
}

export interface BlockerItem {
  description: string
  affects_count: number
  severity: 'low' | 'medium' | 'high'
}

export interface AtRiskItem {
  person: string
  open_commitments: number
  blocking_count: number
  risk_score: number
}

export interface GraphDataResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphStats {
  person:  number
  team:    number
  action:  number
  topic:   number
  blocker: number
}

export interface WebSocketGraphUpdate {
  type: 'graph_update'
  new_nodes: GraphNode[]
  new_edges: GraphEdge[]
}
