import type { Transcript, TranscriptStatus } from '@/types'

const STATUS_MAP: Record<TranscriptStatus, { cls: string; label: string }> = {
  ready:      { cls: 'chip-ready',      label: 'READY'      },
  queued:     { cls: 'chip-queued',     label: 'QUEUED'     },
  processing: { cls: 'chip-processing', label: 'PROCESSING' },
  done:       { cls: 'chip-done',       label: 'PROCESSED'  },
}

interface Props {
  transcript: Transcript
  index: number
  onChange: (id: string, field: keyof Transcript, value: string) => void
  onRemove: (id: string) => void
}

export default function TranscriptCard({ transcript: t, index, onChange, onRemove }: Props) {
  const { cls, label } = STATUS_MAP[t.status]

  return (
    <div className="t-card flex flex-col">
      {/* Header */}
      <div
        className="flex items-center gap-2 px-3 py-2 border-b border-border"
        style={{ background: 'rgba(255,255,255,.02)' }}
      >
        <span
          className="font-mono flex-shrink-0"
          style={{
            fontSize: 9, letterSpacing: 1, color: 'var(--txt-dim)',
            background: 'var(--border)', borderRadius: 2, padding: '1px 5px',
          }}
        >
          #{index + 1}
        </span>

        <input
          className="t-card-input"
          style={{ flex: 2 }}
          value={t.title}
          placeholder="Meeting title…"
          onChange={e => onChange(t.id, 'title', e.target.value)}
        />
        <input
          className="t-card-input mono"
          style={{ flex: 1, maxWidth: 110 }}
          value={t.date}
          placeholder="YYYY-MM-DD"
          onChange={e => onChange(t.id, 'date', e.target.value)}
        />

        <span className={`chip ${cls} font-mono`}>{label}</span>

        <button
          className="rm-btn flex-shrink-0"
          onClick={() => onRemove(t.id)}
          aria-label="Remove transcript"
        >
          ×
        </button>
      </div>

      {/* Body */}
      <div className="px-3 py-2">
        <textarea
          className="card-ta w-full"
          rows={3}
          value={t.text}
          placeholder="Paste transcript text here…"
          onChange={e => onChange(t.id, 'text', e.target.value)}
          style={{ fontFamily: "'IBM Plex Mono', monospace" }}
        />
      </div>

      {/* Progress bar */}
      <div className="t-progress-bar">
        <div className="t-progress-fill" style={{ width: `${t.progress}%` }} />
      </div>
    </div>
  )
}
