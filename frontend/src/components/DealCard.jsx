const categoryConfig = {
  travel: {
    gradient: 'from-blue-500 to-blue-600',
    bgLight: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
      </svg>
    ),
  },
  electronics: {
    gradient: 'from-purple-500 to-purple-600',
    bgLight: 'bg-purple-50',
    text: 'text-purple-700',
    border: 'border-purple-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
    ),
  },
  food: {
    gradient: 'from-orange-500 to-orange-600',
    bgLight: 'bg-orange-50',
    text: 'text-orange-700',
    border: 'border-orange-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
  health: {
    gradient: 'from-emerald-500 to-emerald-600',
    bgLight: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
  },
  fashion: {
    gradient: 'from-pink-500 to-pink-600',
    bgLight: 'bg-pink-50',
    text: 'text-pink-700',
    border: 'border-pink-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
    ),
  },
  MULTI: {
    gradient: 'from-gray-500 to-gray-600',
    bgLight: 'bg-gray-50',
    text: 'text-gray-700',
    border: 'border-gray-200',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
  },
}

const cartContextConfig = {
  single: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Single Item' },
  multi: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Multi-Cart' },
  ambiguous: { bg: 'bg-red-100', text: 'text-red-700', label: 'Ambiguous' },
}

export default function DealCard({ deal, cartContext }) {
  const category = deal.category?.toLowerCase() || 'travel'
  const config = categoryConfig[category] || categoryConfig.travel
  const contextConfig = cartContextConfig[cartContext] || cartContextConfig.single

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-fade-in">
      {/* Gradient header */}
      <div className={`bg-gradient-to-r ${config.gradient} p-4 relative overflow-hidden`}>
        {/* Decorative circles */}
        <div className="absolute -right-4 -top-4 w-24 h-24 bg-white/10 rounded-full" />
        <div className="absolute -right-8 top-8 w-16 h-16 bg-white/10 rounded-full" />

        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-white">
              {config.icon}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{deal.merchant}</h2>
              <p className="text-sm text-white/80 capitalize">{deal.subcategory}</p>
            </div>
          </div>
          {cartContext && (
            <span className={`px-3 py-1.5 text-xs font-semibold rounded-full ${contextConfig.bg} ${contextConfig.text}`}>
              {contextConfig.label}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Category badge */}
        <div className="mb-4">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold ${config.bgLight} ${config.text}`}>
            <span className="w-2 h-2 rounded-full bg-current opacity-60" />
            <span className="capitalize">{deal.category}</span>
          </span>
        </div>

        {/* Deal value - hero number */}
        <div className="mb-5">
          <p className="text-sm font-medium text-gray-500 mb-1">Deal Value</p>
          <div className="flex items-baseline gap-1">
            <span className="text-sm font-semibold text-gray-400">Rs</span>
            <span className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-emerald-600">
              {deal.deal_value?.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Cart items for multi-cart */}
        {deal.cart_items && deal.cart_items.length > 0 && (
          <div className="mb-5">
            <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Cart Items
            </p>
            <div className="space-y-2">
              {deal.cart_items.map((item, idx) => {
                const itemConfig = categoryConfig[item.category?.toLowerCase()] || categoryConfig.travel
                return (
                  <div key={idx} className={`flex items-center justify-between text-sm rounded-xl px-4 py-3 border ${itemConfig.border} ${itemConfig.bgLight}`}>
                    <div className="flex items-center gap-2">
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center ${itemConfig.text} opacity-60`}>
                        {categoryConfig[item.category?.toLowerCase()]?.icon || config.icon}
                      </span>
                      <div>
                        <span className="font-medium text-gray-800">{item.merchant}</span>
                        <span className={`ml-2 text-xs ${itemConfig.text} opacity-70`}>{item.category}</span>
                      </div>
                    </div>
                    <span className="font-bold text-gray-900">Rs {item.deal_value?.toLocaleString('en-IN')}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* User info */}
        {deal.user_history && (
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">User Profile</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">Risk Tier</p>
                <span className={`text-sm font-bold capitalize ${
                  deal.user_history.risk_tier === 'low' ? 'text-emerald-600' :
                  deal.user_history.risk_tier === 'high' ? 'text-red-600' : 'text-amber-600'
                }`}>
                  {deal.user_history.risk_tier}
                </span>
              </div>
              <div className="bg-white rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">Purchases</p>
                <span className="text-sm font-bold text-gray-900">{deal.user_history.total_purchases}</span>
              </div>
            </div>
          </div>
        )}

        {/* Deal ID footer */}
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <p className="text-xs text-gray-400 font-mono">ID: {deal.deal_id}</p>
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Demo Scenario
          </div>
        </div>
      </div>
    </div>
  )
}
