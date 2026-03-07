import type { NodeType, EdgeType } from '@/types'

export const NODE_STYLES: Record<NodeType, {
  r: number
  fill: string
  stroke: string
  icon: string
}> = {
  person:   { r: 20, fill: 'rgba(99,102,241,.18)',  stroke: '#6366f1', icon: '⬡' },
  meeting:  { r: 18, fill: 'rgba(16,185,129,.15)',  stroke: '#10b981', icon: '◈' },
  action:   { r: 15, fill: 'rgba(245,166,35,.15)',  stroke: '#f5a623', icon: '◆' },
  decision: { r: 16, fill: 'rgba(59,130,246,.15)',  stroke: '#3b82f6', icon: '▣' },
  blocker:  { r: 14, fill: 'rgba(239,68,68,.15)',   stroke: '#ef4444', icon: '⚠' },
  topic:    { r: 13, fill: 'rgba(139,92,246,.15)',  stroke: '#8b5cf6', icon: '◉' },
}

export const EDGE_STYLES: Record<EdgeType, {
  stroke: string
  dash: string
  width: number
  markerId: string
}> = {
  committed:   { stroke: 'rgba(99,102,241,.55)',  dash: '',    width: 1.5, markerId: 'mc' },
  originated:  { stroke: 'rgba(16,185,129,.45)',  dash: '',    width: 1.2, markerId: 'mo' },
  blocks:      { stroke: 'rgba(239,68,68,.6)',    dash: '5,4', width: 1.6, markerId: 'mb' },
  contradicts: { stroke: 'rgba(245,166,35,.65)',  dash: '7,3', width: 1.8, markerId: 'mx' },
}

export const LEGEND_ITEMS: { label: string; color: string }[] = [
  { label: 'Person',   color: '#6366f1' },
  { label: 'Meeting',  color: '#10b981' },
  { label: 'Action',   color: '#f5a623' },
  { label: 'Decision', color: '#3b82f6' },
  { label: 'Blocker',  color: '#ef4444' },
  { label: 'Topic',    color: '#8b5cf6' },
]

// Marker definitions for SVG arrowheads
export const MARKER_DEFS: { id: string; fill: string }[] = [
  { id: 'ma', fill: 'rgba(37,51,71,.95)' },
  { id: 'mc', fill: 'rgba(99,102,241,.8)' },
  { id: 'mb', fill: 'rgba(239,68,68,.8)' },
  { id: 'mx', fill: 'rgba(245,166,35,.8)' },
  { id: 'mo', fill: 'rgba(16,185,129,.65)' },
]
