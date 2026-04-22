/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Syne"', 'sans-serif'],
      },
      colors: {
        surface: {
          DEFAULT: '#0c0c0f',
          1: '#111116',
          2: '#18181f',
          3: '#1f1f28',
          4: '#26262f',
        },
        border: '#2a2a35',
        accent: {
          DEFAULT: '#6366f1',
          hover: '#818cf8',
          dim: '#6366f120',
        },
        cyan: {
          DEFAULT: '#22d3ee',
          dim: '#22d3ee18',
        },
        emerald: {
          DEFAULT: '#34d399',
          dim: '#34d39918',
        },
        amber: {
          DEFAULT: '#fbbf24',
          dim: '#fbbf2418',
        },
        rose: {
          DEFAULT: '#fb7185',
          dim: '#fb718518',
        },
        muted: '#6b7280',
        subtle: '#9ca3af',
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
                         linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px)`,
        'glow-accent': 'radial-gradient(circle at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 60%)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.4s ease forwards',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        'shimmer': 'shimmer 1.5s infinite',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(99,102,241,0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(99,102,241,0.6)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        blink: { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0 } },
      },
    },
  },
  plugins: [],
}
