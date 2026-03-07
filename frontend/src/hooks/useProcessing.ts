import { useState, useCallback, useRef } from 'react'
import type { Transcript, ExtractStep, GraphNode, GraphEdge } from '@/types'
import { PROCESS_STEPS } from '@/lib/seedData'
import { apiClient } from '@/lib/api'

let stepIdCounter = 0
const nextId = () => `step-${stepIdCounter++}`

interface UseProcessingReturn {
  processing: boolean
  allDone: boolean
  steps: ExtractStep[]
  showDelta: boolean
  runProcessing: (
    transcripts: Transcript[],
    setTranscripts: React.Dispatch<React.SetStateAction<Transcript[]>>,
    onNewNodes: (nodes: GraphNode[], edges: GraphEdge[]) => void,
  ) => void
}

export function useProcessing(): UseProcessingReturn {
  const [processing, setProcessing] = useState(false)
  const [allDone, setAllDone] = useState(false)
  const [steps, setSteps] = useState<ExtractStep[]>([])
  const [showDelta, setShowDelta] = useState(false)
  const tickerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const runProcessing = useCallback((
    transcripts: Transcript[],
    setTranscripts: React.Dispatch<React.SetStateAction<Transcript[]>>,
    onNewNodes: (nodes: GraphNode[], edges: GraphEdge[]) => void,
  ) => {
    if (processing) return

    setProcessing(true)
    setSteps([])

    // Mark pending transcripts as processing
    setTranscripts(prev =>
      prev.map(t => t.status !== 'done' ? { ...t, status: 'processing' as const } : t)
    )

    // Animate progress bars
    let prog = 0
    tickerRef.current = setInterval(() => {
      prog = Math.min(prog + Math.random() * 11, 93)
      setTranscripts(prev =>
        prev.map(t => t.status === 'processing' ? { ...t, progress: Math.round(prog) } : t)
      )
    }, 280)

    // Stream extraction steps (UI feedback while request is in flight)
    PROCESS_STEPS.forEach((s, i) => {
      setTimeout(() => {
        setSteps(prev => [...prev, { ...s, id: nextId() }])
      }, 200 + i * 420)
    })

    const notes = transcripts.map(t => t.text).join('\n\n---\n\n')

    apiClient
      .processNotes({ notes, nodes: [], edges: [], status: '' })
      .then(() => apiClient.getGraph())
      .then((graphData) => {
        if (tickerRef.current) clearInterval(tickerRef.current)
        setTranscripts(prev =>
          prev.map(t => ({ ...t, status: 'done' as const, progress: 100 }))
        )
        setProcessing(false)
        setAllDone(true)
        setShowDelta(true)
        onNewNodes(graphData.nodes ?? [], graphData.edges ?? [])
      })
      .catch((err) => {
        if (tickerRef.current) clearInterval(tickerRef.current)
        setTranscripts(prev =>
          prev.map(t => t.status === 'processing' ? { ...t, status: 'ready' as const, progress: 0 } : t)
        )
        setProcessing(false)
        setSteps(prev => [...prev, {
          id: nextId(),
          cls: 'warn',
          icon: '⚠',
          text: `Process failed · ${err?.response?.data?.detail ?? err?.message ?? 'Unknown error'}`,
        }])
      })
  }, [processing])

  return { processing, allDone, steps, showDelta, runProcessing }
}
