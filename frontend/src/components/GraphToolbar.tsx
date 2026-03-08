import { LEGEND_ITEMS } from '@/lib/graphConfig'

interface GraphToolbarProps {
  onRefresh?: () => void
}

export default function GraphToolbar({ onRefresh }: GraphToolbarProps) {
  return (
    <div
      className="flex items-center gap-3 flex-shrink-0 border-b border-border"
      style={{ height: 38, padding: '0 16px', background: 'var(--surface)' }}
    >
      <span
        className="font-mono"
        style={{ fontSize: 10, letterSpacing: '1.5px', color: 'var(--txt-dim)', textTransform: 'uppercase' }}
      >
        Knowledge Graph
      </span>
      <span
        className="font-mono opacity-60"
        style={{ fontSize: 9, color: 'var(--txt-dim)', letterSpacing: .5 }}
      >
        drag nodes · click to highlight
      </span>

      <div className="flex items-center gap-3 ml-auto">
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-1 px-2 py-1 text-xs font-mono bg-surface-hover hover:bg-surface-active rounded border border-border transition-colors"
            title="Refresh graph data"
          >
            ↻ Refresh
          </button>
        )}
        {LEGEND_ITEMS.map(l => (
          <div key={l.label} className="flex items-center gap-1">
            <span
              style={{
                width: 7, height: 7, borderRadius: '50%',
                background: l.color, display: 'inline-block', flexShrink: 0,
              }}
            />
            <span
              className="font-mono"
              style={{ fontSize: 9, color: 'var(--txt-dim)', letterSpacing: .5 }}
            >
              {l.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
