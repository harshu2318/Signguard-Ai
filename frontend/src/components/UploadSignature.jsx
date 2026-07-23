import { useState, useRef, useCallback } from 'react'
import { Upload, ImageIcon, X, Sparkles, AlertCircle } from 'lucide-react'
import { uploadSignature } from '../api/api'
import LoadingSpinner from './LoadingSpinner'

const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']

/**
 * UploadSignature — drag-and-drop signature upload card.
 *
 * Props:
 *   onPrediction(result): called with { prediction, confidence, filename }
 *                         after a successful prediction.
 */
export default function UploadSignature({ onPrediction }) {
  const [file,       setFile]       = useState(null)
  const [preview,    setPreview]    = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)

  const fileInputRef = useRef(null)

  // ── File handler ──────────────────────────────────────────────────────────
  const handleFile = useCallback((selectedFile) => {
    if (!selectedFile) return

    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      setError('Unsupported format. Please upload PNG, JPG, BMP, or TIFF.')
      return
    }

    setError(null)
    setFile(selectedFile)

    const reader = new FileReader()
    reader.onloadend = () => setPreview(reader.result)
    reader.readAsDataURL(selectedFile)
  }, [])

  // ── Drag-and-drop handlers ────────────────────────────────────────────────
  const handleDragOver  = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave = ()  => setIsDragging(false)
  const handleDrop      = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  // ── Predict ───────────────────────────────────────────────────────────────
  const handlePredict = async () => {
    if (!file || loading) return
    setLoading(true)
    setError(null)

    try {
      const result = await uploadSignature(file)
      onPrediction(result)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(detail || 'Prediction failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  // ── Reset ─────────────────────────────────────────────────────────────────
  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6
      hover:shadow-xl transition-shadow duration-300">

      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700
          flex items-center justify-center shadow-md shadow-blue-200">
          <Upload className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Upload Signature</h2>
          <p className="text-xs text-slate-400">PNG · JPG · BMP · TIFF</p>
        </div>
      </div>

      {/* Drop Zone / Preview */}
      {!preview ? (
        <div
          id="drop-zone"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center
            justify-center cursor-pointer transition-all duration-200 select-none
            ${isDragging
              ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg shadow-blue-100'
              : 'border-slate-200 bg-slate-50/70 hover:border-blue-400 hover:bg-blue-50/50'
            }
          `}
        >
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4
            transition-colors duration-200
            ${isDragging ? 'bg-blue-100' : 'bg-slate-100'}`}
          >
            <ImageIcon className={`w-8 h-8 transition-colors duration-200
              ${isDragging ? 'text-blue-500' : 'text-slate-400'}`}
            />
          </div>

          <p className="text-slate-600 font-medium text-sm text-center">
            {isDragging ? 'Drop it here!' : 'Drag & drop your signature'}
          </p>
          <p className="text-slate-400 text-xs mt-1">or</p>

          <button
            id="browse-btn"
            type="button"
            className="mt-3 px-5 py-2 bg-blue-600 text-white text-sm font-medium
              rounded-lg hover:bg-blue-700 active:scale-95 transition-all duration-150
              shadow-md shadow-blue-200 pointer-events-none"
          >
            Browse Files
          </button>

          <input
            ref={fileInputRef}
            id="file-input"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <div className="space-y-3 animate-fade-in-up">
          {/* Preview image */}
          <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-50">
            <img
              src={preview}
              alt="Signature preview"
              className="w-full h-48 object-contain p-4"
            />
            <button
              id="remove-image-btn"
              onClick={handleReset}
              className="absolute top-2 right-2 w-8 h-8 bg-white rounded-full shadow-md
                flex items-center justify-center hover:bg-red-50 hover:text-red-500
                text-slate-400 transition-all duration-150 active:scale-90"
              title="Remove image"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-slate-400 truncate pl-1">
            📎 {file?.name}
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl
          flex items-start gap-2 animate-fade-in-up">
          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-600 leading-snug">{error}</p>
        </div>
      )}

      {/* Predict Button */}
      <button
        id="predict-btn"
        onClick={handlePredict}
        disabled={!file || loading}
        className={`
          mt-5 w-full py-3 px-6 rounded-xl font-semibold text-sm
          flex items-center justify-center gap-2 transition-all duration-200
          ${!file || loading
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-200/60 hover:shadow-xl hover:shadow-blue-200 hover:from-blue-700 hover:to-blue-800 active:scale-95'
          }
        `}
      >
        {loading ? (
          <>
            <LoadingSpinner size="sm" color="text-blue-400" />
            <span>Analyzing signature…</span>
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4" />
            <span>Predict Signature</span>
          </>
        )}
      </button>
    </div>
  )
}
