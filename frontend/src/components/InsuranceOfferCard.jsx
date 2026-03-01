import { useState } from 'react'
import ABVariantRenderer from './ABVariantRenderer'

export default function InsuranceOfferCard({
  product,
  quote,
  copyString,
  variant,
  sessionId,
  onConvert
}) {
  const [converting, setConverting] = useState(false)
  const [converted, setConverted] = useState(false)

  const handleConvert = async () => {
    if (converted || converting) return

    setConverting(true)
    try {
      const response = await fetch('/api/ab-events/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          product_id: product.product_id,
        }),
      })

      if (response.ok) {
        setConverted(true)
        onConvert?.()
      }
    } catch (error) {
      console.error('Conversion failed:', error)
    } finally {
      setConverting(false)
    }
  }

  // Calculate value ratio if quote exists
  const valueRatio = quote ? Math.round(quote.coverage_inr / quote.premium_inr) : 0

  return (
    <div className={`bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up transition-all duration-300 ${
      converted ? 'ring-2 ring-green-500 ring-offset-2' : 'hover:shadow-xl'
    }`}>
      {/* Header with gradient accent */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5" />
        <div className="relative p-5 pb-4">
          <div className="flex items-start justify-between">
            <div>
              <ABVariantRenderer variant={variant} />
              <h3 className="text-lg font-bold text-gray-900 mt-2">{product.product_name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${
                        i < Math.round(product.confidence * 5) ? 'bg-primary' : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-500">
                  {(product.confidence * 100).toFixed(0)}% match
                </span>
              </div>
            </div>
            {/* Shield icon */}
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
              converted ? 'bg-green-100 text-green-600' : 'bg-primary/10 text-primary'
            }`}>
              {converted ? (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Copy string - hero text */}
      <div className="px-5">
        <div className="relative bg-gradient-to-br from-gray-50 to-orange-50/50 rounded-xl p-4 border border-orange-100/50">
          <div className="absolute top-3 left-3">
            <svg className="w-4 h-4 text-primary/30" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/>
            </svg>
          </div>
          <p className="text-lg font-semibold text-gray-800 leading-snug pl-4">
            {copyString || product.reason}
          </p>
        </div>
      </div>

      {/* Quote details */}
      {quote && (
        <div className="px-5 py-4">
          <div className="grid grid-cols-2 gap-3">
            {/* Premium - emphasized */}
            <div className="bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl p-4 border border-primary/10">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Premium</p>
              <div className="flex items-baseline gap-1">
                <span className="text-xs font-medium text-gray-400">Rs</span>
                <span className="text-3xl font-extrabold text-primary">{quote.premium_inr}</span>
              </div>
            </div>

            {/* Coverage */}
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Coverage</p>
              <div className="flex items-baseline gap-1">
                <span className="text-xs font-medium text-gray-400">Rs</span>
                <span className="text-xl font-bold text-gray-800">{quote.coverage_inr?.toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>

          {/* Value ratio highlight */}
          {valueRatio > 0 && (
            <div className="mt-3 flex items-center justify-center gap-2 py-2 px-3 bg-emerald-50 rounded-lg border border-emerald-100">
              <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-sm font-semibold text-emerald-700">
                {valueRatio}x value on your premium
              </span>
            </div>
          )}
        </div>
      )}

      {/* Policy info */}
      {quote && (
        <div className="px-5 pb-4">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{quote.validity_days} days validity</span>
            </div>
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{quote.policy_type}</span>
            </div>
          </div>
        </div>
      )}

      {/* CTA Button */}
      <div className="p-5 pt-2">
        <button
          onClick={handleConvert}
          disabled={converting || converted}
          className={`w-full py-4 rounded-xl font-bold text-white text-lg transition-all duration-300 flex items-center justify-center gap-2 ${
            converted
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 cursor-default'
              : converting
              ? 'bg-primary/70 cursor-wait'
              : 'bg-gradient-to-r from-primary to-primary-dark hover:shadow-lg hover:shadow-primary/30 active:scale-[0.98]'
          }`}
        >
          {converted ? (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Protected!</span>
            </>
          ) : converting ? (
            <>
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>Get Covered for Rs {quote?.premium_inr || '---'}</span>
            </>
          )}
        </button>
      </div>

      {/* Product ID footer */}
      <div className="px-5 pb-4">
        <p className="text-xs text-gray-400 text-center font-mono">
          Product: {product.product_id}
        </p>
      </div>
    </div>
  )
}
