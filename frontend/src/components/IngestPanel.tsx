import { useRef, useState } from 'react'
import type { Transcript, ExtractStep } from '@/types'
import TranscriptCard from './TranscriptCard'

interface DeltaItem {
  cls: string
  labelColor: string
  label: string
  text: React.ReactNode
}

const DELTA_ITEMS: DeltaItem[] = [
  {
    cls: 'delta-overdue',
    labelColor: '#ff4d6a',
    label: '⏱ Overdue',
    text: <><strong>Alice</strong> · payments-service refactor · was due Mar 5 · <strong>+7 days</strong></>,
  },
  {
    cls: 'delta-contra',
    labelColor: '#818cf8',
    label: '⚡ Contradiction',
    text: <><strong>Export feature</strong> · contradicts deprioritise decision from Sprint Planning (Mar 5)</>,
  },
  {
    cls: 'delta-blocker',
    labelColor: '#f5a623',
    label: '🔒 Blocker',
    text: <><strong>3 people</strong> blocked pending Alice's payments merge</>,
  },
]

interface Props {
  transcripts: Transcript[]
  onAdd: (files: File[]) => void
  onChange: (id: string, field: keyof Transcript, value: string) => void
  onRemove: (id: string) => void
  onProcess: () => void
  processing: boolean
  allDone: boolean
  steps: ExtractStep[]
  showDelta: boolean
}

export default function IngestPanel({
  transcripts, onAdd, onChange, onRemove,
  onProcess, processing, allDone, steps, showDelta,
}: Props) {
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    onAdd([...e.dataTransfer.files])
  }

  const total   = transcripts.length
  const done    = transcripts.filter(t => t.status === 'done').length
  const pending = total - done

  const btnClass = allDone
    ? 'btn-process done flex-1'
    : 'btn-process flex-1'

  return (
    <div className="flex flex-col overflow-hidden flex-1">

      {/* ── Scrollable queue ── */}
      <div className="flex flex-col gap-3 overflow-y-auto flex-1 p-4">

        {/* Drop zone */}
        <div
          className={`drop-zone p-4 flex-shrink-0${dragOver ? ' over' : ''}`}
          onClick={() => fileRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <span style={{ fontSize: 22, opacity: .45 }}>⊕</span>
          <p className="font-mono text-center leading-relaxed" style={{ fontSize: 10, color: 'var(--txt-dim)', letterSpacing: .8 }}>
            <span style={{ color: 'var(--accent)' }}>Click to upload</span> or drag &amp; drop .txt / .md files
            <br />Multiple transcripts supported
          </p>
        </div>
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".txt,.md"
          className="hidden"
          onChange={e => { onAdd([...(e.target.files ?? [])]); e.target.value = '' }}
        />

        {/* Cards */}
        {transcripts.map((t, i) => (
          <TranscriptCard
            key={t.id}
            transcript={t}
            index={i}
            onChange={onChange}
            onRemove={onRemove}
          />
        ))}
      </div>

      {/* ── Queue footer ── */}
      <div className="flex items-center gap-3 border-t border-border px-4 py-2.5 flex-shrink-0">
        <p className="font-mono whitespace-nowrap" style={{ fontSize: 10, color: 'var(--txt-dim)', letterSpacing: .5 }}>
          <strong style={{ color: 'var(--txt)' }}>{total}</strong> transcripts &nbsp;·&nbsp;
          <strong style={{ color: 'var(--green)' }}>{done}</strong> processed &nbsp;·&nbsp;
          <strong style={{ color: 'var(--amber)' }}>{pending}</strong> pending
        </p>
        <button
          className={btnClass}
          onClick={onProcess}
          disabled={processing || allDone || total === 0}
        >
          {allDone ? '✓ ALL PROCESSED' : processing ? '◌  PROCESSING…' : '⚡ PROCESS ALL'}
        </button>
      </div>

      {/* ── Extraction feed ── */}
      {steps.length > 0 && (
        <div
          className="flex flex-col gap-1 overflow-y-auto flex-shrink-0 border-t border-border"
          style={{ maxHeight: 150, padding: '8px 16px' }}
        >
          {steps.map(s => {
            const parts = s.text.split('·')
            return (
              <div key={s.id} className={`e-step e-step-${s.cls}`}>
                <span className="flex-shrink-0" style={{ fontSize: 12, marginTop: 1 }}>{s.icon}</span>
                <span className="flex-1 leading-relaxed" style={{ color: 'var(--txt-mid)' }}>
                  <strong style={{ color: 'var(--txt)' }}>{parts[0]}</strong>
                  {parts.length > 1 && '·' + parts.slice(1).join('·')}
                </span>
                {s.tag && (
                  <span
                    className="font-mono flex-shrink-0"
                    style={{ fontSize: 9, padding: '1px 5px', borderRadius: 2, background: 'rgba(255,255,255,.05)', color: 'var(--txt-mid)' }}
                  >
                    {s.tag}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* ── Delta report ── */}
      {showDelta && (
        <div className="flex flex-col gap-2 border-t border-border flex-shrink-0 px-4 py-3">
          <p className="font-mono" style={{ fontSize: 9, letterSpacing: '1.5px', color: 'var(--txt-dim)', textTransform: 'uppercase' }}>
            Δ Delta Report
          </p>
          {DELTA_ITEMS.map(d => (
            <div key={d.label} className={`delta-card ${d.cls}`}>
              <p className="font-mono" style={{ fontSize: 9, letterSpacing: 1, textTransform: 'uppercase', color: d.labelColor }}>
                {d.label}
              </p>
              <p style={{ fontSize: 11, color: 'var(--txt-mid)', lineHeight: 1.55, marginTop: 2 }}>
                {d.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
