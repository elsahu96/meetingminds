import { useState, useCallback, useRef } from 'react'
import type { Transcript, ExtractStep, GraphNode, GraphEdge } from '@/types'
import { PROCESS_STEPS } from '@/lib/seedData'

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

    // Stream extraction steps
    PROCESS_STEPS.forEach((s, i) => {
      setTimeout(() => {
        setSteps(prev => [...prev, { ...s, id: nextId() }])
      }, 200 + i * 420)
    })

    const totalMs = 200 + PROCESS_STEPS.length * 420 + 300
    setTimeout(() => {
      if (tickerRef.current) clearInterval(tickerRef.current)

      setTranscripts(prev =>
        prev.map(t => ({ ...t, status: 'done' as const, progress: 100 }))
      )
      setProcessing(false)
      setAllDone(true)
      setShowDelta(true)

      // Add a new node to the graph to demonstrate live update
      onNewNodes(
        [{
          id: 'a21',
          type: 'action',
          label: 'payments+1day',
          overdue: true,
          tooltip: {
            type: 'ACTION',
            name: 'Payments (+1 day)',
            role: 'Alice · Mar 13',
            commits: 'pending',
            risk: 'medium',
          },
        }],
        [{ source: 'alice', target: 'a21', type: 'committed' }],
      )
    }, totalMs)
  }, [processing])

  return { processing, allDone, steps, showDelta, runProcessing }
}
