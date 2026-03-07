import { useState, useRef, useEffect } from 'react'
import type { ChatMessage } from '@/types'
import { SEED_CHAT } from '@/lib/seedData'

let msgIdCounter = 200
const nextId = () => `msg-${msgIdCounter++}`

interface Props {
  onHighlight: (nodeId: string) => void
}

export default function ChatPanel({ onHighlight }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>(SEED_CHAT)
  const [input, setInput]       = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = () => {
    const text = input.trim()
    if (!text) return
    setInput('')

    const userMsg: ChatMessage = {
      id: nextId(), role: 'user', text, timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])

    setTimeout(() => {
      const agentMsg: ChatMessage = {
        id: nextId(),
        role: 'agent',
        text: `Based on the knowledge graph, <span class="hl-pill">Alice Chen</span> carries the highest risk with 4 open commitments. The payments refactor is <span style="color:#ff4d6a">7 days overdue</span> and blocking 3 team members.`,
        citations: [
          { label: 'action:a17', nodeId: 'a17' },
          { label: 'person:alice', nodeId: 'alice' },
        ],
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, agentMsg])
    }, 800)
  }

  return (
    <div className="flex flex-col overflow-hidden flex-1">

      {/* Messages */}
      <div className="flex flex-col gap-4 overflow-y-auto flex-1 p-4">
        {messages.map(m => (
          <div
            key={m.id}
            className={`flex flex-col gap-1 animate-fadeSlide ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`rounded ${m.role === 'user' ? 'bubble-user' : 'bubble-agent'}`}
              style={{ maxWidth: '88%', padding: '10px 14px', lineHeight: 1.65, fontSize: 13 }}
              dangerouslySetInnerHTML={{ __html: m.text }}
            />

            {m.citations && m.citations.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {m.citations.map((c, i) => (
                  <span
                    key={i}
                    className="cite-pill font-mono"
                    onClick={() => c.nodeId && onHighlight(c.nodeId)}
                  >
                    {c.label}
                  </span>
                ))}
              </div>
            )}

            <p className="font-mono" style={{ fontSize: 9, letterSpacing: .5, color: 'var(--txt-dim)' }}>
              {m.role === 'agent'
                ? `MeetingMind · ${m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                : m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              }
            </p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2 border-t border-border p-3">
        <input
          className="chat-input flex-1"
          value={input}
          placeholder="Ask about commitments, blockers, decisions…"
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <button className="btn-send rounded" onClick={send}>SEND</button>
      </div>
    </div>
  )
}
