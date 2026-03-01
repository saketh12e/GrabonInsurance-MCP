import { useState, useEffect } from 'react'
import DealCard from './DealCard'
import InsuranceOfferCard from './InsuranceOfferCard'
import ConversionDashboard from './ConversionDashboard'
import CartScenarioDemo from './CartScenarioDemo'

export default function InsuranceStorefront() {
  const [activeTab, setActiveTab] = useState('demo') // 'demo' | 'standard'
  const [selectedDeal, setSelectedDeal] = useState(null)
  const [classification, setClassification] = useState(null)
  const [quotes, setQuotes] = useState({})
  const [copyStrings, setCopyStrings] = useState({})
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [refreshDashboard, setRefreshDashboard] = useState(0)

  // Generate session ID on mount
  useEffect(() => {
    setSessionId(crypto.randomUUID())
  }, [])

  // Classify deal and get quotes when deal is selected
  useEffect(() => {
    if (!selectedDeal) return

    const processDeal = async () => {
      setLoading(true)
      setError(null)

      try {
        // Classify the deal
        const classifyResponse = await fetch('/api/classify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            merchant: selectedDeal.merchant,
            category: selectedDeal.category,
            subcategory: selectedDeal.subcategory,
            deal_value: selectedDeal.deal_value,
            user_history: selectedDeal.user_history,
            cart_items: selectedDeal.cart_items,
          }),
        })

        if (!classifyResponse.ok) {
          const err = await classifyResponse.json()
          throw new Error(err.detail || 'Classification failed')
        }

        const classResult = await classifyResponse.json()
        setClassification(classResult)

        // Get quotes for each product
        if (classResult.show_offer && classResult.top_products?.length > 0) {
          const quotesMap = {}
          const copyMap = {}

          for (const product of classResult.top_products) {
            // Get quote
            const quoteResponse = await fetch('/api/quote', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                product_id: product.product_id,
                deal_value: selectedDeal.deal_value,
                risk_tier: selectedDeal.user_history?.risk_tier || 'medium',
              }),
            })

            if (quoteResponse.ok) {
              quotesMap[product.product_id] = await quoteResponse.json()
            }

            // Get variant and generate copy
            const variantResponse = await fetch(
              `/api/ab-events/variant?session_id=${sessionId}&product_id=${product.product_id}`
            )
            const variantData = await variantResponse.json()

            // Generate copy
            const copyResponse = await fetch('/api/generate-copy', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                product_id: product.product_id,
                product_name: product.product_name,
                deal_description: `${selectedDeal.merchant} ${selectedDeal.subcategory} Rs ${selectedDeal.deal_value}`,
                premium_inr: quotesMap[product.product_id]?.premium_inr || 0,
                variant: variantData.variant,
              }),
            })

            if (copyResponse.ok) {
              const copyData = await copyResponse.json()
              copyMap[product.product_id] = {
                copy: copyData.copy_string,
                variant: copyData.variant,
                sessionId: copyData.session_id,
              }

              // Record impression
              await fetch('/api/ab-events/impression', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  session_id: copyData.session_id,
                  deal_id: selectedDeal.deal_id,
                  user_id: 'demo-user',
                  product_id: product.product_id,
                  copy_string: copyData.copy_string,
                }),
              })
            }
          }

          setQuotes(quotesMap)
          setCopyStrings(copyMap)
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    processDeal()
  }, [selectedDeal, sessionId])

  const handleConversion = () => {
    // Trigger dashboard refresh
    setRefreshDashboard(prev => prev + 1)
  }

  return (
    <div className="space-y-8">
      {/* Tab navigation */}
      <div className="bg-white rounded-xl shadow-sm p-1.5 inline-flex gap-1">
        <button
          onClick={() => setActiveTab('demo')}
          className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
            activeTab === 'demo'
              ? 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-md'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Cart Scenario Demo
        </button>
        <button
          onClick={() => setActiveTab('standard')}
          className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
            activeTab === 'standard'
              ? 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-md'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          Standard View
        </button>
      </div>

      {/* Main content area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column - Deal selection and card */}
        <div className="space-y-6">
          {activeTab === 'demo' && (
            <CartScenarioDemo
              onSelectDeal={setSelectedDeal}
              selectedDealId={selectedDeal?.deal_id}
            />
          )}

          {selectedDeal && (
            <DealCard
              deal={selectedDeal}
              cartContext={classification?.cart_context}
            />
          )}

          {!selectedDeal && (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a Deal</h3>
              <p className="text-gray-500 text-sm">
                Choose a deal scenario above to see the insurance recommendation
              </p>
            </div>
          )}
        </div>

        {/* Right column - Insurance offers */}
        <div className="space-y-6">
          {loading && (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <div className="relative w-16 h-16 mx-auto mb-4">
                <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Analyzing Deal</h3>
              <p className="text-gray-500 text-sm">Finding the best insurance options...</p>
            </div>
          )}

          {error && (
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl shadow-lg p-6 border border-red-200">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-red-200 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-red-800">Error Occurred</p>
                  <p className="text-red-600 text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {!loading && classification && !classification.show_offer && (
            <div className="bg-gradient-to-br from-amber-50 to-yellow-100 rounded-2xl shadow-lg p-6 border border-yellow-200">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-yellow-200 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-yellow-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-yellow-800">No Offer Available</p>
                  <p className="text-yellow-700 text-sm mt-1">
                    {classification.reason || 'Deal value too low for insurance offer'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {!loading && classification?.show_offer && classification.top_products?.map((product, index) => (
            <InsuranceOfferCard
              key={product.product_id}
              product={product}
              quote={quotes[product.product_id]}
              copyString={copyStrings[product.product_id]?.copy}
              variant={copyStrings[product.product_id]?.variant}
              sessionId={copyStrings[product.product_id]?.sessionId}
              onConvert={handleConversion}
            />
          ))}

          {!loading && !selectedDeal && (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-primary/10 to-primary/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Insurance Offers</h3>
              <p className="text-gray-500 text-sm">
                Personalized recommendations will appear here
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Bottom - A/B Dashboard */}
      <ConversionDashboard refreshTrigger={refreshDashboard} />
    </div>
  )
}
