const variantConfig = {
  urgency: {
    label: 'Urgency',
    bgClass: 'bg-gradient-to-r from-red-50 to-orange-50',
    textClass: 'text-red-700',
    borderClass: 'border-red-200',
    dotClass: 'bg-red-500',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  value: {
    label: 'Value',
    bgClass: 'bg-gradient-to-r from-green-50 to-emerald-50',
    textClass: 'text-green-700',
    borderClass: 'border-green-200',
    dotClass: 'bg-green-500',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  social_proof: {
    label: 'Social Proof',
    bgClass: 'bg-gradient-to-r from-blue-50 to-indigo-50',
    textClass: 'text-blue-700',
    borderClass: 'border-blue-200',
    dotClass: 'bg-blue-500',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
}

export default function ABVariantRenderer({ variant }) {
  const config = variantConfig[variant] || variantConfig.value

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full border ${config.bgClass} ${config.textClass} ${config.borderClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotClass} animate-pulse`} />
      {config.icon}
      <span>A/B: {config.label}</span>
    </span>
  )
}
