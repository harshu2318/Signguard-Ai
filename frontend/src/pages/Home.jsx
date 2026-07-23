import { useState } from 'react'
import UploadSignature from '../components/UploadSignature'
import PredictionCard  from '../components/PredictionCard'
import ChatBot         from '../components/ChatBot'

/**
 * Home — main page with two-column layout.
 *
 * Left  : Upload card → Prediction card (stacked)
 * Right : AI Chatbot (full height)
 *
 * The `prediction` state is the single source of truth shared by both sides.
 */
export default function Home() {
  const [prediction, setPrediction] = useState(null)

  const handlePrediction = (result) => {
    setPrediction(result)
  }

  const handleReset = () => {
    setPrediction(null)
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* ── Hero Text ── */}
      <div className="text-center mb-10">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-800 tracking-tight">
          Handwritten Signature{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-blue-400">
            Verification
          </span>
        </h1>
        <p className="mt-3 text-slate-500 text-base max-w-xl mx-auto">
          Upload a signature image to instantly verify if it's&nbsp;
          <span className="font-semibold text-emerald-600">genuine</span> or&nbsp;
          <span className="font-semibold text-red-500">forged</span> — then chat
          with our AI assistant for a full explanation.
        </p>
      </div>

      {/* ── Two-Column Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

        {/* Left Column */}
        <div className="flex flex-col gap-6">
          <UploadSignature onPrediction={handlePrediction} />

          {prediction && (
            <PredictionCard
              prediction={prediction}
              onReset={handleReset}
            />
          )}

          {/* Info banner when no prediction yet */}
          {!prediction && (
            <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5">
              <p className="text-sm text-blue-700 font-medium mb-1">💡 How it works</p>
              <ol className="text-sm text-blue-600 space-y-1 list-decimal list-inside">
                <li>Upload a handwritten signature image</li>
                <li>The AI model classifies it as Genuine or Forged</li>
                <li>Chat with the assistant to understand the result</li>
              </ol>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="lg:sticky lg:top-20">
          <ChatBot prediction={prediction} />
        </div>

      </div>

    </main>
  )
}
