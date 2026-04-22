import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Trash2, MessageSquare, Code, Lightbulb } from 'lucide-react'
import { chatAPI } from '../api/client'
import { Spinner, ErrorBanner } from '../components/UI'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

// ─── Render message content (detect ``` code blocks) ─────────────────────────
function MessageContent({ content }) {
  const parts = content.split(/(```[\w]*\n[\s\S]*?```)/g)
  return (
    <div className="space-y-2">
      {parts.map((part, i) => {
        const match = part.match(/```([\w]*)\n([\s\S]*?)```/)
        if (match) {
          const [, lang, code] = match
          return (
            <div key={i} className="rounded-lg overflow-hidden border border-border">
              <SyntaxHighlighter
                language={lang || 'text'}
                style={vscDarkPlus}
                customStyle={{ margin: 0, background: '#111116', padding: '12px', fontSize: '12px' }}
              >
                {code.trim()}
              </SyntaxHighlighter>
            </div>
          )
        }
        return part ? <p key={i} className="whitespace-pre-wrap leading-relaxed">{part}</p> : null
      })}
    </div>
  )
}

// ─── Quick prompt chips ───────────────────────────────────────────────────────
const QUICK_PROMPTS = [
  { label: 'Tech Stack', text: 'What tech stack should I use for a SaaS product?', icon: Lightbulb },
  { label: 'Code Review', text: 'What are best practices for FastAPI project structure?', icon: Code },
  { label: 'Features',   text: 'What features should a modern dashboard include?', icon: MessageSquare },
]

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\'m **ProjectPilot AI** — your expert software engineering assistant.\n\nAsk me anything: architecture decisions, code review, feature planning, tech stack comparisons, or anything about your project.' }
  ])
  const [input, setInput]   = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return

    const userMsg = { role: 'user', content: msg }
    const history = messages
      .filter(m => m.role !== 'assistant' || messages.indexOf(m) > 0) // skip greeting in history
      .slice(-10) // last 10 messages
      .map(m => ({ role: m.role, content: m.content }))

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const { data } = await chatAPI.send(msg, history)
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (e) {
      setError(e.message)
      setMessages(prev => prev.slice(0, -1)) // remove optimistic message
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const clear = () => setMessages([messages[0]])

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto px-6 py-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-white">AI Chat</h1>
          <p className="text-sm text-muted mt-0.5">Powered by Gemini</p>
        </div>
        <button onClick={clear} className="btn-ghost text-xs">
          <Trash2 size={13} /> Clear
        </button>
      </div>

      {/* Quick prompts */}
      {messages.length <= 1 && (
        <div className="flex gap-2 mb-4 flex-wrap">
          {QUICK_PROMPTS.map(({ label, text, icon: Icon }) => (
            <button
              key={label}
              onClick={() => send(text)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-2 border border-border hover:border-accent/40 rounded-lg text-xs text-muted hover:text-white transition-all"
            >
              <Icon size={12} /> {label}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 animate-slide-up ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5
              ${msg.role === 'assistant'
                ? 'bg-accent/20 border border-accent/30'
                : 'bg-surface-3 border border-border'
              }`}
            >
              {msg.role === 'assistant'
                ? <Bot size={14} className="text-accent" />
                : <User size={14} className="text-muted" />
              }
            </div>

            {/* Bubble */}
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm
              ${msg.role === 'assistant'
                ? 'bg-surface-2 border border-border text-subtle'
                : 'bg-accent text-white'
              }`}
            >
              <MessageContent content={msg.content} />
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="w-7 h-7 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center flex-shrink-0">
              <Bot size={14} className="text-accent" />
            </div>
            <div className="bg-surface-2 border border-border rounded-2xl px-4 py-3 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Error */}
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Input */}
      <div className="flex gap-2 mt-2">
        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          placeholder="Ask anything about your project…"
          className="input-base flex-1"
          disabled={loading}
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="btn-primary px-3"
        >
          {loading ? <Spinner size={16} /> : <Send size={16} />}
        </button>
      </div>
      <p className="text-[10px] text-muted text-center mt-2">Enter to send · Shift+Enter for newline</p>
    </div>
  )
}
