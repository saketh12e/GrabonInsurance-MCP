import { useState, useEffect } from 'react'
import InsuranceStorefront from './components/InsuranceStorefront'

function App() {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    // Check API health
    const checkHealth = () => {
      fetch('/api/health')
        .then(res => res.ok ? 'connected' : 'error')
        .then(setApiStatus)
        .catch(() => setApiStatus('disconnected'))
    }

    checkHealth()
    // Poll every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-orange-50/30">
      {/* Header with gradient */}
      <header className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary via-primary-dark to-primary opacity-95" />

        {/* Decorative shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-primary-light/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4 lg:py-5">
            {/* Logo and brand */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg border border-white/30">
                  <span className="text-white font-extrabold text-xl lg:text-2xl">G</span>
                </div>
                {/* Decorative dot */}
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white shadow-sm" />
              </div>
              <div>
                <h1 className="text-xl lg:text-2xl font-bold text-white tracking-tight">
                  GrabOn-Insurance
                </h1>
                <p className="text-xs lg:text-sm text-white/80 font-medium">
                  Contextual Insurance at Checkout
                </p>
              </div>
            </div>

            {/* Status badge */}
            <div className={`flex items-center gap-2.5 px-4 py-2 rounded-full backdrop-blur-sm border transition-all duration-300 ${apiStatus === 'connected'
              ? 'bg-green-500/20 border-green-400/30 text-green-100'
              : apiStatus === 'checking'
                ? 'bg-yellow-500/20 border-yellow-400/30 text-yellow-100'
                : 'bg-red-500/20 border-red-400/30 text-red-100'
              }`}>
              <span className={`relative flex h-2.5 w-2.5`}>
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${apiStatus === 'connected' ? 'bg-green-400' :
                  apiStatus === 'checking' ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${apiStatus === 'connected' ? 'bg-green-400' :
                  apiStatus === 'checking' ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
              </span>
              <span className="text-sm font-medium">
                {apiStatus === 'connected' ? 'API Connected' :
                  apiStatus === 'checking' ? 'Connecting...' : 'API Disconnected'}
              </span>
            </div>
          </div>

          {/* Hero section */}
          <div className="pb-8 lg:pb-12">
            <div className="max-w-2xl">
              <h2 className="text-2xl lg:text-3xl font-bold text-white mb-2">
                Smart Insurance for Every Deal
              </h2>
              <p className="text-white/70 text-sm lg:text-base">
                Real-time insurance recommendations powered by AI. Protect your purchases with the right coverage at the right price.
              </p>
            </div>
          </div>
        </div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-8 lg:h-12">
            <path d="M0 60V20C360 60 720 0 1080 20C1260 30 1380 40 1440 60V60H0Z" fill="#F8F9FA" />
          </svg>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8 -mt-2">
        <InsuranceStorefront />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="text-sm text-gray-600">
                GrabOn VibeCoder Challenge 2025
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-500">
              <span className="hidden sm:inline">Project 02: Contextual Embedded Insurance</span>
              <span className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
