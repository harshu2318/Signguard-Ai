import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, MessageCircle, Lightbulb } from 'lucide-react'
import { sendMessage } from '../api/api'

// ── Typing indicator (three bouncing dots) ────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </div>
  )
}

// ── Simple text formatter: render newlines as line breaks ─────────────────────
function MessageText({ text }) {
  const lines = text.split('\n')
  return (
    <span>
      {lines.map((line, i) => (
        <span key={i}>
          {line}
          {i < lines.length - 1 && <br />}
        </span>
      ))}
    </span>
  )
}

// ── Suggested questions shown before the user starts chatting ─────────────────
const SUGGESTIONS = [
  'How does signature verification work?',
  'What features are used for classification?',
  'Explain the confidence score.',
  'What are common forgery indicators?',
]

const INITIAL_MESSAGE = {
  id:   0,
  role: 'assistant',
  text: "Hello! I'm SignGuard AI Assistant 👋\n\nUpload a signature and predict it first, then ask me anything — why it was classified a certain way, how the model works, or anything about signature verification!",
}

/**
 * ChatBot — scrollable RAG-powered chat interface.
 *
 * Props:
 *   prediction: { prediction: string, confidence: number } | null
 */
export default function ChatBot({ prediction }) {
  const [messages, setMessages] = useState([INITIAL_MESSAGE])
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef       = useRef(null)
  const prevPredRef    = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Acknowledge new predictions automatically
  useEffect(() => {
    if (!prediction) return
    // Only trigger when the prediction actually changes (avoid on re-renders)
    const key = `${prediction.prediction}-${prediction.confidence}`
    if (prevPredRef.current === key) return
    prevPredRef.current = key

    setMessages((prev) => [
      ...prev,
      {
        id:   Date.now(),
        role: 'assistant',
        text: `✅ Prediction received!\n\nVerdict: ${prediction.prediction}\nConfidence: ${prediction.confidence}%\n\nFeel free to ask me why this signature was classified as ${prediction.prediction.toLowerCase()}!`,
      },
    ])
  }, [prediction])

  // ── Send a message ─────────────────────────────────────────────────────────
  const handleSend = async (text) => {
    const question = (text ?? input).trim()
    if (!question || loading) return

    // Append user message immediately
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', text: question }])
    setInput('')
    setLoading(true)

    try {
      const data = await sendMessage({
        question,
        prediction: prediction?.prediction ?? null,
        confidence: prediction?.confidence ?? null,
      })
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', text: data.answer },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id:   Date.now() + 1,
          role: 'assistant',
          text: '⚠️ Sorry, I encountered an error. Please check that the backend is running and the vector database has been built.',
        },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const showSuggestions = messages.length <= 1

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-100
      flex flex-col h-[700px] hover:shadow-xl transition-shadow duration-300">

      {/* ── Header ── */}
      <div className="flex items-center gap-3 p-5 border-b border-slate-100 flex-shrink-0">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700
          flex items-center justify-center shadow-md shadow-blue-200">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-slate-800">AI Assistant</h2>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse-slow" />
            <span className="text-xs text-slate-400">
              Powered by RAG · Groq · ChromaDB
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50
          text-blue-600 text-xs font-medium rounded-full border border-blue-100">
          <MessageCircle className="w-3.5 h-3.5" />
          {messages.length - 1} msg{messages.length !== 2 ? 's' : ''}
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-fade-in-up`}
          >
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center
              ${msg.role === 'user'
                ? 'bg-gradient-to-br from-blue-500 to-blue-700 shadow-md shadow-blue-200'
                : 'bg-slate-100 border border-slate-200'
              }`}
            >
              {msg.role === 'user'
                ? <User className="w-4 h-4 text-white" />
                : <Bot className="w-4 h-4 text-slate-500" />
              }
            </div>

            {/* Bubble */}
            <div className={`
              max-w-[82%] px-4 py-3 rounded-2xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-sm shadow-md shadow-blue-100'
                : 'bg-slate-50 text-slate-700 rounded-tl-sm border border-slate-100'
              }
            `}>
              <MessageText text={msg.text} />
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-2.5 animate-fade-in-up">
            <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200
              flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-slate-500" />
            </div>
            <div className="bg-slate-50 rounded-2xl rounded-tl-sm border border-slate-100">
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Suggested Questions ── */}
      {showSuggestions && (
        <div className="px-4 pb-3 flex-shrink-0">
          <div className="flex items-center gap-1.5 mb-2">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
            <p className="text-xs text-slate-400 font-medium">Try asking:</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((q) => (
              <button
                key={q}
                id={`suggestion-${q.slice(0, 10).replace(/\s/g, '-')}`}
                onClick={() => handleSend(q)}
                disabled={loading}
                className="text-xs px-3 py-1.5 bg-blue-50 text-blue-600 rounded-full
                  border border-blue-100 hover:bg-blue-100 active:scale-95
                  transition-all duration-150 disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Input ── */}
      <div className="p-4 border-t border-slate-100 flex-shrink-0">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            id="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about signature verification…"
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 text-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              placeholder-slate-400 disabled:bg-slate-50 disabled:text-slate-400
              transition-all duration-150"
          />
          <button
            id="send-btn"
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className={`p-3 rounded-xl transition-all duration-150
              ${!input.trim() || loading
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-md shadow-blue-200 hover:shadow-lg hover:shadow-blue-200 active:scale-90'
              }
            `}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-slate-300 mt-2 text-center">
          Answers grounded in the research paper via RAG
        </p>
      </div>

    </div>
  )
}
