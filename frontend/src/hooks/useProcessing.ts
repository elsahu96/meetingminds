import { useState, useCallback } from 'react'
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
  const [allDone,    setAllDone]    = useState(false)
  const [steps,      setSteps]      = useState<ExtractStep[]>([])
  const [showDelta,  setShowDelta]  = useState(false)

  const runProcessing = useCallback((
    transcripts: Transcript[],
    setTranscripts: React.Dispatch<React.SetStateAction<Transcript[]>>,
    onNewNodes: (nodes: GraphNode[], edges: GraphEdge[]) => void,
  ) => {
    if (processing) return

    const toProcess = transcripts.filter(t => t.status !== 'done')
    if (!toProcess.length) return

    setProcessing(true)
    setAllDone(false)
    setSteps([])

    // First file → processing, all others → queued
    setTranscripts(prev => prev.map(t => {
      if (t.status === 'done') return t
      return t.id === toProcess[0].id
        ? { ...t, status: 'processing' as const, progress: 0 }
        : { ...t, status: 'queued' as const, progress: 0 }
    }))

    // Stream UI extraction steps while requests are in flight
    PROCESS_STEPS.forEach((s, i) => {
      setTimeout(() => setSteps(prev => [...prev, { ...s, id: nextId() }]), 200 + i * 420)
    })

    const processSequentially = async (queue: Transcript[]) => {
      for (let i = 0; i < queue.length; i++) {
        const current = queue[i]

        // Animate progress bar only for the current file
        let prog = 0
        const ticker = setInterval(() => {
          prog = Math.min(prog + Math.random() * 11, 93)
          setTranscripts(prev =>
            prev.map(t => t.id === current.id ? { ...t, progress: Math.round(prog) } : t)
          )
        }, 280)

        try {
          await apiClient.processNotes({ notes: current.text, nodes: [], edges: [], status: '' })
          clearInterval(ticker)

          // Mark current done; advance next to processing
          setTranscripts(prev => prev.map(t => {
            if (t.id === current.id)         return { ...t, status: 'done'       as const, progress: 100 }
            if (t.id === queue[i + 1]?.id)   return { ...t, status: 'processing' as const, progress: 0   }
            return t
          }))
        } catch (err: unknown) {
          clearInterval(ticker)
          setTranscripts(prev =>
            prev.map(t => t.id === current.id ? { ...t, status: 'ready' as const, progress: 0 } : t)
          )
          setProcessing(false)
          setSteps(prev => [...prev, {
            id:   nextId(),
            cls:  'warn' as const,
            icon: '⚠',
            text: `Process failed · ${
              (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
              ?? (err as { message?: string })?.message
              ?? 'Unknown error'
            }`,
          }])
          return
        }
      }

      // All files done — refresh graph
      try {
        const graphData = await apiClient.getGraph()
        onNewNodes(graphData.nodes ?? [], graphData.edges ?? [])
      } catch { /* graph refresh failure is non-fatal */ }

      setProcessing(false)
      setAllDone(true)
      setShowDelta(true)
    }

    processSequentially(toProcess)
  }, [processing])

  return { processing, allDone, steps, showDelta, runProcessing }
}
