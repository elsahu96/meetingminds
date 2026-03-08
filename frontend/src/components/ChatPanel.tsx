import { useState, useRef, useEffect } from 'react'
import { marked } from 'marked'
import type { ChatMessage, GraphNode, NodeType } from '@/types'
import { SEED_CHAT } from '@/lib/seedData'
import { apiClient } from '@/lib/api'
import { NODE_STYLES } from '@/lib/graphConfig'

marked.setOptions({ breaks: true })

/** Wrap known entity labels in hl-pill spans before markdown processing. */
function highlightEntities(text: string, nodes: GraphNode[]): string {
  if (!nodes.length) return text
  console.log('text:', text)
  console.log('nodes:', nodes)
  // Build label → node map; longest labels first so "Alice Chen" matches before "Alice"
  const labelToNode = new Map<string, GraphNode>()
  for (const node of nodes) {
    if (node.label && node.label.length > 1) labelToNode.set(node.label, node)
  }
  const labels = [...labelToNode.keys()].sort((a, b) => b.length - a.length)

  let result = text
  for (const label of labels) {
    const node = labelToNode.get(label)!
    const style = NODE_STYLES[node.type as NodeType]
    const color = style?.stroke ?? '#94a3b8'
    const bg = style?.fill ?? 'rgba(148,163,184,.12)'
    const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    // Avoid replacing inside existing HTML tags or already-wrapped spans
    result = result.replace(
      new RegExp(`(?<!class="[^"]*|<[^>]*)\\b${escaped}\\b`, 'gi'),
      `<span class="hl-pill" style="color:${color};background:${bg}">${label}</span>`,
    )
  }
  return result
}

function renderAgentText(text: string, nodes: GraphNode[]): string {
  const highlighted = highlightEntities(text, nodes)
  const html = marked.parse(highlighted)
  return typeof html === 'string' ? html : highlighted
}

let msgIdCounter = 200
const nextId = () => `msg-${msgIdCounter++}`

interface Props {
  onHighlight: (nodeId: string) => void
  nodes?: GraphNode[]
}

export default function ChatPanel({ onHighlight, nodes = [] }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>(SEED_CHAT)
  const [input, setInput]       = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const [sending, setSending] = useState(false)

  const send = async () => {
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    setSending(true)

    const userMsg: ChatMessage = {
      id: nextId(), role: 'user', text, timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await apiClient.query({ question: text })
      const citations = (res.citations ?? []).map(c => ({
        label: `${c.entity_type}:${c.entity_id}`,
        nodeId: c.entity_id,
      }))
      const agentMsg: ChatMessage = {
        id: nextId(),
        role: 'agent',
        text: res.answer,
        citations,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, agentMsg])
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } }; message?: string })
        ?.response?.data?.detail ?? (err as { message?: string })?.message ?? 'Unknown error'
      const errorMsg: ChatMessage = {
        id: nextId(),
        role: 'agent',
        text: `<span style="color:#ff4d6a">⚠ Query failed · ${detail}</span>`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setSending(false)
    }
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
              className={`rounded ${m.role === 'user' ? 'bubble-user' : 'bubble-agent'} ${m.role === 'agent' ? 'prose-chat' : ''}`}
              style={{ maxWidth: '88%', padding: '10px 14px', lineHeight: 1.65, fontSize: 13 }}
              dangerouslySetInnerHTML={{ __html: m.role === 'agent' ? renderAgentText(m.text, nodes) : m.text }}
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
          disabled={sending}
        />
        <button className="btn-send rounded" onClick={send} disabled={sending}>
          {sending ? '◌' : 'SEND'}
        </button>
      </div>
    </div>
  )
}
