import React from 'react'

const STATS = [
  { label: 'Meetings',       value: '2',  color: undefined },
  { label: 'People',         value: '4',  color: undefined },
  { label: 'Open Actions',   value: '7',  color: '#f5a623' },
  { label: 'Overdue',        value: '1',  color: '#ff4d6a' },
  { label: 'Contradictions', value: '1',  color: '#818cf8' },
]

export default function StatusBar() {
  return (
    <footer
      className="flex items-center flex-shrink-0 border-t border-border"
      style={{ height: 26, padding: '0 16px', gap: 16, background: 'var(--surface)' }}
    >
      {STATS.map((s, i) => (
        <React.Fragment key={s.label}>
          {i > 0 && <div style={{ width: 1, height: 12, background: 'var(--border)' }} />}
          <div
            className="flex items-center font-mono"
            style={{ fontSize: 9, letterSpacing: .8, color: 'var(--txt-dim)', textTransform: 'uppercase', gap: 4 }}
          >
            {s.label}
            <span style={{ color: s.color ?? 'var(--txt)', fontWeight: 500, marginLeft: 2 }}>
              {s.value}
            </span>
          </div>
        </React.Fragment>
      ))}

      <a
        href="#"
        className="flex items-center ml-auto font-mono"
        style={{ fontSize: 9, color: 'var(--txt-dim)', textDecoration: 'none', letterSpacing: .8, gap: 5, transition: 'color .15s' }}
        onMouseEnter={e => (e.currentTarget.style.color = 'var(--accent)')}
        onMouseLeave={e => (e.currentTarget.style.color = 'var(--txt-dim)')}
      >
        <span
          className="animate-pulse inline-block"
          style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green)' }}
        />
        LANGSMITH TRACE ACTIVE
      </a>
    </footer>
  )
}
