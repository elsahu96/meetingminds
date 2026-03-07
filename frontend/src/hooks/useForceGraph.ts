import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import type { GraphNode, GraphEdge } from '@/types'
import { NODE_STYLES, EDGE_STYLES, MARKER_DEFS } from '@/lib/graphConfig'

interface Dims { w: number; h: number }

export function useForceGraph(
  svgRef: React.RefObject<SVGSVGElement>,
  containerRef: React.RefObject<HTMLDivElement>,
  nodes: GraphNode[],
  edges: GraphEdge[],
  highlighted: string | null,
  onHighlight: (id: string | null) => void,
  onTooltip: (payload: { node: GraphNode; x: number; y: number } | null) => void,
) {
  const simRef  = useRef<d3.Simulation<GraphNode, GraphEdge> | null>(null)
  const liveRef = useRef<GraphNode[]>([])
  const rafRef  = useRef<ReturnType<typeof setInterval> | null>(null)
  const [dims, setDims] = useState<Dims>({ w: 800, h: 600 })

  // Observe container size
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect
      setDims({ w: Math.round(width), h: Math.round(height) })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [containerRef])

  // Rebuild simulation when nodes/edges/dims change
  useEffect(() => {
    const svg = svgRef.current
    if (!svg || dims.w === 0) return

    const sel = d3.select(svg)

    // Carry over existing positions
    const simNodes: GraphNode[] = nodes.map(n => {
      const old = liveRef.current.find(e => e.id === n.id)
      return old
        ? { ...n, x: old.x, y: old.y, vx: old.vx, vy: old.vy }
        : { ...n, x: dims.w * (0.25 + Math.random() * 0.5), y: dims.h * (0.25 + Math.random() * 0.5) }
    })
    const simEdges: GraphEdge[] = edges.map(e => ({ ...e }))

    simRef.current?.stop()
    if (rafRef.current) clearInterval(rafRef.current)

    // ── Defs ──
    sel.selectAll('defs').remove()
    const defs = sel.append('defs')

    MARKER_DEFS.forEach(({ id, fill }) => {
      defs.append('marker')
        .attr('id', id).attr('markerWidth', 7).attr('markerHeight', 7)
        .attr('refX', 6).attr('refY', 3.5).attr('orient', 'auto')
        .append('polygon').attr('points', '0,0 7,3.5 0,7').attr('fill', fill)
    })

    const addGlowFilter = (id: string, blur: number) => {
      const f = defs.append('filter').attr('id', id)
      f.append('feGaussianBlur').attr('stdDeviation', blur).attr('result', 'blur')
      const m = f.append('feMerge')
      m.append('feMergeNode').attr('in', 'blur')
      m.append('feMergeNode').attr('in', 'SourceGraphic')
    }
    addGlowFilter('gf',   3.5)
    addGlowFilter('gfhl', 5.5)

    // ── Layers ──
    sel.selectAll('.edge-layer, .node-layer').remove()
    const edgeG = sel.append('g').attr('class', 'edge-layer')
    const nodeG = sel.append('g').attr('class', 'node-layer')

    const linkSel = edgeG.selectAll<SVGLineElement, GraphEdge>('line')
      .data(simEdges).enter().append('line')

    const nodeGroups = nodeG.selectAll<SVGGElement, GraphNode>('g.node')
      .data(simNodes, (d: GraphNode) => d.id)
      .enter().append('g')
      .attr('class', 'node')
      .style('cursor', 'grab')
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on('start', (event, d) => {
            if (!event.active) simRef.current?.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = Math.max(25, Math.min(dims.w - 25, event.x))
            d.fy = Math.max(25, Math.min(dims.h - 25, event.y))
          })
          .on('end', (event, d) => {
            if (!event.active) simRef.current?.alphaTarget(0)
            d.fx = null; d.fy = null
          })
      )
      .on('mouseenter', (event, d) => {
        onTooltip({ node: d, x: event.clientX, y: event.clientY })
      })
      .on('mousemove', (event) => {
        onTooltip(prev => prev ? { ...prev, x: event.clientX, y: event.clientY } : null)
      })
      .on('mouseleave', () => onTooltip(null))
      .on('click', (event, d) => {
        event.stopPropagation()
        onHighlight(highlighted === d.id ? null : d.id)
      })

    nodeGroups.append('circle').attr('class', 'pulse-ring')
    nodeGroups.append('circle').attr('class', 'hl-ring')
    nodeGroups.append('circle').attr('class', 'main-circle')
    nodeGroups.append('text').attr('class', 'node-icon')
    nodeGroups.append('text').attr('class', 'node-label')

    // ── Force simulation ──
    const simulation = d3.forceSimulation<GraphNode, GraphEdge>(simNodes)
      .force('link',
        d3.forceLink<GraphNode, GraphEdge>(simEdges)
          .id(d => d.id)
          .distance(115)
          .strength(0.4)
      )
      .force('charge', d3.forceManyBody<GraphNode>().strength(-320))
      .force('center',  d3.forceCenter<GraphNode>(dims.w / 2, dims.h / 2).strength(0.04))
      .force('collide', d3.forceCollide<GraphNode>().radius(d => (NODE_STYLES[d.type]?.r ?? 16) + 14))
      .alphaDecay(0.025)

    simRef.current = simulation

    simulation.on('tick', () => {
      // Clamp
      simNodes.forEach(n => {
        const r = NODE_STYLES[n.type]?.r ?? 16
        n.x = Math.max(r + 5, Math.min(dims.w - r - 5, n.x ?? dims.w / 2))
        n.y = Math.max(r + 5, Math.min(dims.h - r - 5, n.y ?? dims.h / 2))
      })

      // Update edges
      linkSel.each(function(d) {
        const es = EDGE_STYLES[(d.type as string) as keyof typeof EDGE_STYLES] ?? EDGE_STYLES.committed
        const src = d.source as GraphNode
        const tgt = d.target as GraphNode
        const ra = NODE_STYLES[src.type]?.r ?? 16
        const rb = NODE_STYLES[tgt.type]?.r ?? 16
        const dx = (tgt.x ?? 0) - (src.x ?? 0)
        const dy = (tgt.y ?? 0) - (src.y ?? 0)
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const s = d3.select(this)
          .attr('x1', (src.x ?? 0) + (dx / dist) * ra)
          .attr('y1', (src.y ?? 0) + (dy / dist) * ra)
          .attr('x2', (tgt.x ?? 0) - (dx / dist) * (rb + 7))
          .attr('y2', (tgt.y ?? 0) - (dy / dist) * (rb + 7))
          .attr('stroke', es.stroke)
          .attr('stroke-width', es.width)
          .attr('opacity', 0.9)
          .attr('marker-end', `url(#${es.markerId})`)
        if (es.dash) s.attr('stroke-dasharray', es.dash)
        else s.attr('stroke-dasharray', null)
      })

      // Update nodes
      nodeGroups.each(function(d) {
        const g   = d3.select(this)
        const ns  = NODE_STYLES[d.type] ?? NODE_STYLES.action
        const isHl = d.id === highlighted
        const isOd = !!d.overdue
        const stroke = isOd ? '#ff4d6a' : ns.stroke
        const fill   = isOd ? 'rgba(255,77,106,.2)' : ns.fill
        const r  = isHl ? ns.r + 4 : ns.r
        const cx = d.x ?? 0, cy = d.y ?? 0

        g.select('.pulse-ring')
          .attr('cx', cx).attr('cy', cy).attr('r', r + 8)
          .attr('fill', 'none')
          .attr('stroke', isOd ? 'rgba(255,77,106,.22)' : 'none')
          .attr('stroke-width', 1.5)
          .style('display', isOd ? '' : 'none')

        g.select('.hl-ring')
          .attr('cx', cx).attr('cy', cy).attr('r', r + 9)
          .attr('fill', 'none').attr('stroke', stroke)
          .attr('stroke-width', 1).attr('opacity', 0.35)
          .style('display', isHl ? '' : 'none')

        g.select('.main-circle')
          .attr('cx', cx).attr('cy', cy).attr('r', r)
          .attr('fill', fill).attr('stroke', stroke)
          .attr('stroke-width', isHl ? 2.8 : 1.8)
          .attr('filter', isHl ? 'url(#gfhl)' : 'url(#gf)')

        g.select('.node-icon')
          .attr('x', cx).attr('y', cy + 4)
          .attr('text-anchor', 'middle').attr('font-size', 11)
          .attr('fill', stroke).attr('font-family', 'IBM Plex Mono,monospace')
          .attr('pointer-events', 'none').text(ns.icon)

        g.select('.node-label')
          .attr('x', cx).attr('y', cy + r + 13)
          .attr('text-anchor', 'middle').attr('font-size', 9)
          .attr('fill', 'rgba(122,150,176,.8)').attr('font-family', 'IBM Plex Mono,monospace')
          .attr('letter-spacing', 0.3).attr('pointer-events', 'none').text(d.label)
      })

      liveRef.current = simNodes
    })

    // Pulsing animation for overdue rings
    let frame = 0
    rafRef.current = setInterval(() => {
      frame++
      const t = (Math.sin(frame * 0.05) + 1) / 2
      nodeG.selectAll<SVGCircleElement, GraphNode>('.pulse-ring')
        .filter(d => !!d.overdue)
        .attr('r', d => {
          const base = (NODE_STYLES[d.type]?.r ?? 15) + (d.id === highlighted ? 4 : 0)
          return base + 5 + t * 7
        })
        .attr('opacity', 0.5 - t * 0.38)
    }, 40)

    // Click background to clear highlight
    sel.on('click', () => onHighlight(null))

    return () => {
      simulation.stop()
      if (rafRef.current) clearInterval(rafRef.current)
    }
  }, [nodes, edges, dims])

  // Re-style only (no simulation restart) when highlighted changes
  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return
    d3.select(svg).select('.node-layer')
      .selectAll<SVGGElement, GraphNode>('g.node')
      .each(function(d) {
        const g  = d3.select(this)
        const ns = NODE_STYLES[d.type] ?? NODE_STYLES.action
        const isHl = d.id === highlighted
        const r  = isHl ? ns.r + 4 : ns.r
        const isOd = !!d.overdue
        const stroke = isOd ? '#ff4d6a' : ns.stroke
        g.select('.hl-ring').style('display', isHl ? '' : 'none').attr('r', r + 9)
        g.select('.main-circle').attr('r', r).attr('stroke-width', isHl ? 2.8 : 1.8)
          .attr('stroke', stroke).attr('filter', isHl ? 'url(#gfhl)' : 'url(#gf)')
      })
  }, [highlighted, svgRef])

  return { dims }
}
