/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF6B2B',
        'primary-dark': '#E55A1F',
        'primary-light': '#FF8A52',
        background: '#F8F9FA',
        surface: '#FFFFFF',
        'surface-hover': '#FAFBFC',
        accent: {
          blue: '#3B82F6',
          green: '#10B981',
          purple: '#8B5CF6',
          pink: '#EC4899',
          orange: '#F59E0B',
          red: '#EF4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'glow': '0 0 20px rgba(255, 107, 43, 0.3)',
        'glow-sm': '0 0 10px rgba(255, 107, 43, 0.2)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'bounce-subtle': 'bounceSubtle 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-card': 'linear-gradient(135deg, #fff 0%, #f8f9fa 100%)',
        'gradient-primary': 'linear-gradient(135deg, #FF6B2B 0%, #FF8A52 100%)',
        'gradient-hero': 'linear-gradient(135deg, #FF6B2B 0%, #E55A1F 50%, #FF8A52 100%)',
      },
    },
  },
  plugins: [],
}
