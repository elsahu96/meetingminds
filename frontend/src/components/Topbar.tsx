interface Props {
  transcriptCount: number
}

export default function Topbar({ transcriptCount }: Props) {
  return (
    <header
      className="flex items-center gap-4 flex-shrink-0 border-b border-border"
      style={{ height: 44, padding: '0 20px', background: 'var(--surface)' }}
    >
      {/* Logo */}
      <h1
        className="font-display"
        style={{ fontSize: 22, letterSpacing: 2, color: 'var(--accent)', textShadow: '0 0 20px rgba(0,212,255,0.18)' }}
      >
        Meeting<span style={{ color: 'var(--txt-mid)' }}>Mind</span>
      </h1>

      <div style={{ width: 1, height: 20, background: 'var(--border)' }} />

      <span className="badge-live font-mono">● LIVE</span>
      <span className="badge-db font-mono">SURREALDB</span>

      <div style={{ width: 1, height: 20, background: 'var(--border)' }} />

      <span
        className="font-mono"
        style={{ fontSize: 10, color: 'var(--txt-dim)', letterSpacing: .5 }}
      >
        {transcriptCount} transcript{transcriptCount !== 1 ? 's' : ''} loaded
      </span>

      {/* Right side */}
      <div className="flex items-center gap-3 ml-auto">
        <div className="risk-badge">
          <span
            className="animate-pulse inline-block"
            style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--red)' }}
          />
          <span className="font-mono" style={{ fontSize: 10 }}>
            RISK: alice_chen · 4 open commitments
          </span>
        </div>

        <button className="btn-top">LANGSMITH ↗</button>
        <button className="btn-top">EXPORT</button>
      </div>
    </header>
  )
}
