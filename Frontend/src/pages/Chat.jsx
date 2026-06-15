import { useEffect, useRef, useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-3 py-2">
      <div className="typing-dot" />
      <div className="typing-dot" />
      <div className="typing-dot" />
    </div>
  )
}

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`chat-message flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      {!isUser && <span className="text-xl mr-2 mt-1">🤖</span>}
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-drinkoo-600 text-white rounded-br-sm'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
        }`}
      >
        <p className="whitespace-pre-wrap">{msg.content}</p>
        {msg.context && (
          <details className="mt-2 text-xs opacity-70">
            <summary className="cursor-pointer hover:opacity-100">View retrieved context</summary>
            <pre className="mt-1 whitespace-pre-wrap font-mono text-xs overflow-auto max-h-40">{msg.context}</pre>
          </details>
        )}
      </div>
    </div>
  )
}

const SUGGESTED = [
  'Which DRINKOO products are low sugar?',
  'What ingredients are in the citrus drinks?',
  'Are there active promotions for sparkling beverages?',
  'What should I do if my order arrives damaged?',
]

export default function Chat() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'assistant',
      content: `Hi ${user?.full_name?.split(' ')[0] || 'there'}! 👋 I'm the DRINKOO assistant. Ask me anything about our beverages, ingredients, promotions, or support policies.`,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (question) => {
    const q = (question || input).trim()
    if (!q || loading) return

    setInput('')
    setError('')
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: q }])
    setLoading(true)

    try {
      const { data } = await api.post('/chat', { question: q })
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.answer,
          context: data.retrieved_context,
        },
      ])
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-5rem)]">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-drinkoo-100 flex items-center justify-center text-xl">🤖</div>
        <div>
          <h1 className="font-semibold text-gray-900">DRINKOO Assistant</h1>
          <p className="text-xs text-drinkoo-500">● Online — Powered by OpenRouter RAG</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto pr-1">
        {messages.map((msg) => (
          <ChatBubble key={msg.id} msg={msg} />
        ))}
        {loading && (
          <div className="flex justify-start mb-3">
            <span className="text-xl mr-2 mt-1">🤖</span>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm shadow-sm">
              <TypingIndicator />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="error-text text-center mb-2">{error}</p>}

      {/* Suggestions (only on first message) */}
      {messages.length === 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {SUGGESTED.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="text-xs bg-drinkoo-50 text-drinkoo-700 border border-drinkoo-200 rounded-full px-3 py-1 hover:bg-drinkoo-100 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2 mt-2">
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about DRINKOO products, ingredients, promotions…"
          disabled={loading}
          className="input-field resize-none flex-1"
          style={{ minHeight: '44px', maxHeight: '120px' }}
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="btn-primary px-5 self-end"
        >
          Send
        </button>
      </div>
      <p className="text-xs text-gray-400 text-center mt-1">
        Answers are grounded in DRINKOO data only.
      </p>
    </div>
  )
}
