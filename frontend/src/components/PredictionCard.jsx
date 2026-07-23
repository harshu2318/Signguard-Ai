import { useState, useEffect } from 'react'
import { ShieldCheck, ShieldAlert, RefreshCw, TrendingUp, CheckCircle2 } from 'lucide-react'

/**
 * PredictionCard — displays the ML prediction result with animated confidence bar.
 *
 * Props:
 *   prediction: { prediction: string, confidence: number, filename: string }
 *   onReset():  called when user wants to upload another image
 */
export default function PredictionCard({ prediction, onReset }) {
  const [barWidth, setBarWidth] = useState(0)

  // Animate the confidence bar on mount / when prediction changes
  useEffect(() => {
    if (!prediction) return
    setBarWidth(0)
    const timer = setTimeout(() => setBarWidth(prediction.confidence), 100)
    return () => clearTimeout(timer)
  }, [prediction])

  if (!prediction) return null

  const isGenuine = prediction.prediction === 'Genuine'

  // ── Colour tokens based on verdict ───────────────────────────────────────
  const colors = isGenuine
    ? {
        iconBg:   'bg-gradient-to-br from-emerald-400 to-emerald-600',
        cardBorder:'border-emerald-100',
        verdictBg: 'bg-emerald-50',
        verdictTxt:'text-emerald-600',
        barBg:     'bg-emerald-500',
        badge:     'bg-emerald-100 text-emerald-700 border-emerald-200',
        scoreTxt:  'text-emerald-600',
      }
    : {
        iconBg:   'bg-gradient-to-br from-red-400 to-red-600',
        cardBorder:'border-red-100',
        verdictBg: 'bg-red-50',
        verdictTxt:'text-red-600',
        barBg:     'bg-red-500',
        badge:     'bg-red-100 text-red-700 border-red-200',
        scoreTxt:  'text-red-600',
      }

  return (
    <div className={`bg-white rounded-2xl shadow-lg border ${colors.cardBorder} p-6
      animate-fade-in-up hover:shadow-xl transition-shadow duration-300`}>

      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-10 h-10 rounded-xl ${colors.iconBg}
          flex items-center justify-center shadow-md`}>
          {isGenuine
            ? <ShieldCheck className="w-5 h-5 text-white" />
            : <ShieldAlert className="w-5 h-5 text-white" />
          }
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Prediction Result</h2>
          <p className="text-xs text-slate-400">AI Analysis Complete</p>
        </div>
        <div className={`ml-auto px-2.5 py-1 text-xs font-medium rounded-full border ${colors.badge}`}>
          {isGenuine ? '✓ Verified' : '⚠ Suspicious'}
        </div>
      </div>

      {/* Verdict Panel */}
      <div className={`${colors.verdictBg} rounded-xl p-5 mb-4 text-center`}>
        <div className="flex items-center justify-center gap-2 mb-1">
          <CheckCircle2 className={`w-5 h-5 ${colors.verdictTxt}`} />
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
            Verdict
          </p>
        </div>
        <p className={`text-4xl font-extrabold ${colors.verdictTxt} tracking-tight`}>
          {prediction.prediction}
        </p>
        {prediction.filename && (
          <p className="text-xs text-slate-400 mt-2 truncate">
            📎 {prediction.filename}
          </p>
        )}
      </div>

      {/* Confidence Bar */}
      <div className="mb-5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-600">
              Confidence Score
            </span>
          </div>
          <span className={`text-xl font-bold ${colors.scoreTxt}`}>
            {prediction.confidence}%
          </span>
        </div>

        {/* Animated bar */}
        <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full ${colors.barBg} rounded-full transition-all duration-1000 ease-out`}
            style={{ width: `${barWidth}%` }}
          />
        </div>

        <p className="text-xs text-slate-400 mt-2">
          The model is&nbsp;
          <span className={`font-semibold ${colors.scoreTxt}`}>
            {prediction.confidence}% confident
          </span>
          &nbsp;this signature is&nbsp;
          <span className="font-medium">{prediction.prediction.toLowerCase()}</span>.
        </p>
      </div>

      {/* Reset Button */}
      <button
        id="reset-btn"
        onClick={onReset}
        className="w-full py-2.5 px-4 border-2 border-slate-200 rounded-xl
          text-slate-500 font-medium text-sm flex items-center justify-center gap-2
          hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50
          active:scale-95 transition-all duration-150"
      >
        <RefreshCw className="w-4 h-4" />
        Upload Another Image
      </button>
    </div>
  )
}
