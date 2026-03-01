import { useState, useEffect } from 'react'

const variantStyles = {
  urgency: {
    dot: 'bg-red-500',
    bar: 'from-red-400 to-red-500',
    light: 'bg-red-50',
    text: 'text-red-700',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  value: {
    dot: 'bg-green-500',
    bar: 'from-green-400 to-green-500',
    light: 'bg-green-50',
    text: 'text-green-700',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  social_proof: {
    dot: 'bg-blue-500',
    bar: 'from-blue-400 to-blue-500',
    light: 'bg-blue-50',
    text: 'text-blue-700',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
}

export default function ConversionDashboard({ refreshTrigger }) {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/ab-events/dashboard')
      if (!response.ok) throw new Error('Failed to fetch dashboard')
      const data = await response.json()
      setDashboard(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [refreshTrigger])

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-gray-200 rounded-xl" />
          <div className="h-6 bg-gray-200 rounded w-48" />
        </div>
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-100 rounded-xl" />
          ))}
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center gap-3 text-red-600 mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="font-medium">Error: {error}</span>
        </div>
        <button
          onClick={fetchDashboard}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary border border-primary rounded-lg hover:bg-primary/5 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retry
        </button>
      </div>
    )
  }

  const maxImpressions = Math.max(...(dashboard?.variants?.map(v => v.impressions) || [1]))

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary/10 to-primary/20 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">A/B Testing Dashboard</h3>
              <p className="text-sm text-gray-500">Real-time variant performance</p>
            </div>
          </div>
          <button
            onClick={fetchDashboard}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/5 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4 p-6 bg-gray-50/50">
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span className="text-sm font-medium text-gray-500">Impressions</span>
          </div>
          <p className="text-3xl font-extrabold text-gray-900">
            {dashboard?.total_impressions || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium text-gray-500">Conversions</span>
          </div>
          <p className="text-3xl font-extrabold text-emerald-600">
            {dashboard?.total_conversions || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span className="text-sm font-medium text-gray-500">Overall CVR</span>
          </div>
          <p className="text-3xl font-extrabold text-primary">
            {dashboard?.overall_cvr_percent?.toFixed(1) || 0}%
          </p>
        </div>
      </div>

      {/* Variant breakdown */}
      <div className="p-6">
        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Variant Performance</h4>

        {dashboard?.variants && dashboard.variants.length > 0 ? (
          <div className="space-y-4">
            {dashboard.variants.map((stat) => {
              const style = variantStyles[stat.variant] || variantStyles.value
              const barWidth = maxImpressions > 0 ? (stat.impressions / maxImpressions) * 100 : 0

              return (
                <div
                  key={stat.variant}
                  className={`rounded-xl p-4 border transition-all duration-300 ${
                    stat.is_best
                      ? 'bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-200 shadow-sm'
                      : 'bg-white border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${style.light} ${style.text}`}>
                        {style.icon}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900 capitalize">
                            {stat.variant.replace('_', ' ')}
                          </span>
                          {stat.is_best && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold bg-emerald-100 text-emerald-700 rounded-full">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                              Best
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-gray-500">
                          {stat.impressions} impressions • {stat.conversions} conversions
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-2xl font-bold ${stat.is_best ? 'text-emerald-600' : 'text-gray-900'}`}>
                        {stat.cvr_percent.toFixed(1)}%
                      </span>
                      <p className="text-xs text-gray-500">CVR</p>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${style.bar} transition-all duration-500`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-gray-500 font-medium">No A/B test data yet</p>
            <p className="text-sm text-gray-400 mt-1">Select a deal to start testing variants</p>
          </div>
        )}
      </div>
    </div>
  )
}
