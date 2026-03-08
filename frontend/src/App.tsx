import { useState, useCallback, useEffect } from 'react'
import type { Transcript, GraphNode, GraphEdge, GraphStats } from '@/types'
import { SEED_TRANSCRIPTS } from '@/lib/seedData'
import { useProcessing } from '@/hooks/useProcessing'
import { apiClient } from '@/lib/api'
import Topbar        from '@/components/Topbar'
import StatusBar     from '@/components/StatusBar'
import GraphToolbar  from '@/components/GraphToolbar'
import ForceGraph    from '@/components/ForceGraph'
import IngestPanel   from '@/components/IngestPanel'
import ChatPanel     from '@/components/ChatPanel'

type Tab = 'ingest' | 'query'

let fileIdCounter = 10
const nextFileId  = () => `t${fileIdCounter++}`

export default function App() {
  const [tab,          setTab]          = useState<Tab>('ingest')
  const [transcripts,  setTranscripts]  = useState<Transcript[]>([])
  const [graphNodes,   setGraphNodes]   = useState<GraphNode[]>([])
  const [graphEdges,   setGraphEdges]   = useState<GraphEdge[]>([])
  const [highlighted,    setHighlighted]    = useState<string | null>(null)
  const [focusedNodeIds, setFocusedNodeIds] = useState<string[] | null>(null)
  const [stats,          setStats]          = useState<GraphStats>({ person: 0, team: 0, action: 0, topic: 0, blocker: 0 })

  const { processing, allDone, steps, showDelta, runProcessing } = useProcessing()

  // Refresh stats whenever graph nodes are loaded/updated
  useEffect(() => {
    if (graphNodes.length === 0) return
    apiClient.getStats().then(setStats).catch(() => {})
  }, [graphNodes])


  // Function to refresh graph data — also clears any query focus
  const refreshGraph = useCallback(async () => {
    try {
      const graphData = await apiClient.getGraph()
      setGraphNodes(graphData.nodes || [])
      setGraphEdges(graphData.edges || [])
      setFocusedNodeIds(null)
      setHighlighted(null)
    } catch (error) {
      console.error('Failed to refresh graph data:', error)
    }
  }, [])

  // ── Transcript management ──────────────────────────────────────────────────
  const addTranscripts = useCallback((files: File[]) => {
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = e => {
        const t: Transcript = {
          id:       nextFileId(),
          title:    file.name.replace(/\.[^.]+$/, ''),
          date:     new Date().toISOString().slice(0, 10),
          text:     ((e.target?.result as string) ?? '').slice(0, 800),
          status:   'ready',
          progress: 0,
        }
        setTranscripts(prev => [...prev, t])
      }
      reader.readAsText(file)
    })
  }, [])

  const updateTranscript = useCallback((id: string, field: keyof Transcript, value: string) => {
    setTranscripts(prev => prev.map(t => t.id === id ? { ...t, [field]: value } : t))
  }, [])

  const removeTranscript = useCallback((id: string) => {
    setTranscripts(prev => prev.filter(t => t.id !== id))
  }, [])

  // ── Processing ─────────────────────────────────────────────────────────────
  const handleProcess = useCallback(() => {
    runProcessing(transcripts, setTranscripts, (newNodes, newEdges) => {
      setGraphNodes(newNodes)
      setGraphEdges(newEdges)
    })
  }, [transcripts, runProcessing])

  // ── Graph highlight ────────────────────────────────────────────────────────
  const handleHighlight = useCallback((id: string | null) => {
    setHighlighted(id)
  }, [])

  const highlightAndQuery = useCallback((id: string) => {
    setHighlighted(id)
    setTab('query')
  }, [])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar transcriptCount={transcripts.length} />

      <div className="flex flex-1 overflow-hidden">

        {/* ── Left panel ── */}
        <aside
          className="flex flex-col border-r border-border flex-shrink-0"
          style={{ width: 430, background: 'var(--surface)' }}
        >
          {/* Tabs */}
          <div className="flex border-b border-border px-4">
            {(['ingest', 'query'] as Tab[]).map(t => (
              <button
                key={t}
                className={`panel-tab${tab === t ? ' active' : ''}`}
                onClick={() => setTab(t)}
              >
                {t === 'ingest' ? 'INGEST' : 'QUERY AGENT'}
              </button>
            ))}
          </div>

          {tab === 'ingest' && (
            <IngestPanel
              transcripts={transcripts}
              onAdd={addTranscripts}
              onChange={updateTranscript}
              onRemove={removeTranscript}
              onProcess={handleProcess}
              processing={processing}
              allDone={allDone}
              steps={steps}
              showDelta={showDelta}
            />
          )}

          {tab === 'query' && (
            <ChatPanel
              onHighlight={highlightAndQuery}
              onFocusNodes={setFocusedNodeIds}
              nodes={graphNodes}
            />
          )}
        </aside>

        {/* ── Vertical divider ── */}
        <div
          className="flex-shrink-0 transition-colors duration-150 cursor-col-resize"
          style={{ width: 1, background: 'var(--border)' }}
          onMouseEnter={e => (e.currentTarget.style.background = 'var(--accent)')}
          onMouseLeave={e => (e.currentTarget.style.background = 'var(--border)')}
        />

        {/* ── Right panel: graph ── */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <GraphToolbar onRefresh={refreshGraph} />
          <ForceGraph
            nodes={graphNodes}
            edges={graphEdges}
            highlighted={highlighted}
            focusedNodeIds={focusedNodeIds}
            onHighlight={handleHighlight}
          />
        </div>
      </div>

      <StatusBar stats={stats} />
    </div>
  )
}
