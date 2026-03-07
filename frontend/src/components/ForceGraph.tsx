import { useRef, useState } from 'react'
import type { GraphNode, GraphEdge } from '@/types'
import { useForceGraph } from '@/hooks/useForceGraph'

interface Props {
  nodes: GraphNode[]
  edges: GraphEdge[]
  highlighted: string | null
  onHighlight: (id: string | null) => void
}

interface TooltipState {
  node: GraphNode
  x: number
  y: number
}

export default function ForceGraph({ nodes, edges, highlighted, onHighlight }: Props) {
  const svgRef       = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [tooltip, setTooltip] = useState<TooltipState | null>(null)

  const { dims } = useForceGraph(
    svgRef, containerRef, nodes, edges, highlighted, onHighlight,
    (payload) => setTooltip(payload as TooltipState | null),
  )

  return (
    <div ref={containerRef} className="relative flex-1 overflow-hidden graph-bg bg-bg">
      <svg
        ref={svgRef}
        width={dims.w}
        height={dims.h}
        className="absolute inset-0 select-none"
      />

      {tooltip && (
        <div
          className="graph-tooltip animate-fadeSlide font-mono"
          style={{ left: tooltip.x + 14, top: tooltip.y - 10 }}
        >
          <p className="text-txt-dim mb-1" style={{ fontSize: 9, letterSpacing: 1, textTransform: 'uppercase' }}>
            {tooltip.node.tooltip.type}
          </p>
          <p className="text-txt font-medium mb-1.5" style={{ fontSize: 12 }}>
            {tooltip.node.tooltip.name}
          </p>
          <div className="flex justify-between gap-4 text-txt-dim" style={{ fontSize: 10 }}>
            <span>Role</span>
            <span className="text-txt-mid">{tooltip.node.tooltip.role}</span>
          </div>
          <div className="flex justify-between gap-4 text-txt-dim" style={{ fontSize: 10 }}>
            <span>Commits</span>
            <span className="text-txt-mid">{tooltip.node.tooltip.commits}</span>
          </div>
          <div className="flex justify-between gap-4 text-txt-dim" style={{ fontSize: 10 }}>
            <span>Risk</span>
            <span style={{ color: tooltip.node.overdue ? 'var(--tw-color-red, #ff4d6a)' : undefined }}
                  className={tooltip.node.overdue ? '' : 'text-txt-mid'}>
              {tooltip.node.tooltip.risk}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
