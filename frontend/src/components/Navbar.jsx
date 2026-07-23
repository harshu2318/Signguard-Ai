import { Shield } from 'lucide-react'

/**
 * Navbar — top navigation bar with logo and tagline.
 */
export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 glass border-b border-white/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700
              flex items-center justify-center shadow-lg shadow-blue-200">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-800 tracking-tight">
                SignGuard
                <span className="text-blue-600"> AI</span>
              </span>
              <p className="text-xs text-slate-400 leading-none hidden sm:block">
                Signature Verification Platform
              </p>
            </div>
          </div>

          {/* Badge */}
          <div className="flex items-center gap-2">
            <span className="hidden sm:flex items-center gap-1.5 px-3 py-1.5
              bg-blue-50 text-blue-600 text-xs font-medium rounded-full border border-blue-100">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
              RAG Powered
            </span>
            <span className="px-3 py-1.5 bg-slate-100 text-slate-500 text-xs
              font-medium rounded-full border border-slate-200">
              Portfolio Project
            </span>
          </div>

        </div>
      </div>
    </nav>
  )
}
