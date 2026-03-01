import { useState, useEffect } from 'react'

const categoryIcons = {
  travel: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  ),
  electronics: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  ),
  food: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  ),
  health: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  ),
  fashion: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
  ),
  MULTI: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  ),
}

const categoryColors = {
  travel: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100',
  electronics: 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100',
  food: 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100',
  health: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100',
  fashion: 'bg-pink-50 text-pink-700 border-pink-200 hover:bg-pink-100',
  MULTI: 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100',
}

export default function CartScenarioDemo({ onSelectDeal, selectedDealId }) {
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const response = await fetch('/api/deals')
        if (!response.ok) throw new Error('Failed to fetch deals')
        const data = await response.json()
        setDeals(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchDeals()
  }, [])

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gray-200 rounded-xl" />
          <div className="h-6 bg-gray-200 rounded w-40" />
        </div>
        <div className="h-12 bg-gray-200 rounded-xl mb-4" />
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 w-24 bg-gray-200 rounded-full" />
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
          <span className="font-medium">Error loading deals: {error}</span>
        </div>
      </div>
    )
  }

  const selectedDeal = deals.find(d => d.deal_id === selectedDealId)

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary/10 to-primary/20 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Deal Scenarios</h3>
            <p className="text-sm text-gray-500">{deals.length} test scenarios available</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Dropdown selector */}
        <div className="mb-5">
          <label htmlFor="deal-select" className="block text-sm font-semibold text-gray-700 mb-2">
            Select a deal to test:
          </label>
          <div className="relative">
            <select
              id="deal-select"
              value={selectedDealId || ''}
              onChange={(e) => {
                const deal = deals.find(d => d.deal_id === e.target.value)
                if (deal) onSelectDeal(deal)
              }}
              className="w-full px-4 py-3.5 pr-10 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-primary bg-white text-gray-900 appearance-none cursor-pointer transition-colors hover:border-gray-300"
            >
              <option value="">Choose a scenario...</option>
              {deals.map((deal) => (
                <option key={deal.deal_id} value={deal.deal_id}>
                  {deal.deal_id}: {deal.merchant} - Rs {deal.deal_value.toLocaleString('en-IN')} ({deal.category})
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        {/* Quick scenario chips - show all */}
        <div className="mb-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Quick Select</p>
          <div className="flex flex-wrap gap-2">
            {deals.map((deal) => {
              const category = deal.category?.toLowerCase() || 'travel'
              const isSelected = selectedDealId === deal.deal_id
              const colorClass = categoryColors[category] || categoryColors.travel
              const icon = categoryIcons[category] || categoryIcons.travel

              return (
                <button
                  key={deal.deal_id}
                  onClick={() => onSelectDeal(deal)}
                  className={`inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-full border transition-all duration-200 ${
                    isSelected
                      ? 'bg-gradient-to-r from-primary to-primary-dark text-white border-primary shadow-md shadow-primary/20 scale-105'
                      : colorClass
                  }`}
                >
                  {!isSelected && icon}
                  <span>{deal.deal_id}</span>
                  {isSelected && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Expected results hint */}
        {selectedDeal?.expected && (
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-blue-800 mb-1">Expected Output</p>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {selectedDeal.expected.products.map((product) => (
                    <span
                      key={product}
                      className="inline-flex items-center px-2 py-0.5 text-xs font-mono font-medium bg-blue-100 text-blue-700 rounded"
                    >
                      {product}
                    </span>
                  ))}
                </div>
                {selectedDeal.expected.note && (
                  <p className="text-xs text-blue-600">
                    <span className="font-medium">Note:</span> {selectedDeal.expected.note}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
