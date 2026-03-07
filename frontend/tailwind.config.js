/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:        '#080c10',
        surface:   '#0d1219',
        surface2:  '#111820',
        border:    '#1a2433',
        'border-hi': '#253347',
        txt:       '#c8d8e8',
        'txt-dim': '#4a6480',
        'txt-mid': '#7a96b0',
        accent:    '#00d4ff',
        green:     '#00e5a0',
        amber:     '#f5a623',
        red:       '#ff4d6a',
        indigo:    '#818cf8',
      },
      fontFamily: {
        mono:    ['"IBM Plex Mono"', 'monospace'],
        sans:    ['"DM Sans"', 'sans-serif'],
        display: ['"Bebas Neue"', 'sans-serif'],
      },
      boxShadow: {
        glow:    '0 0 20px rgba(0,212,255,0.18)',
        'glow-red': '0 0 16px rgba(255,77,106,0.35)',
      },
      keyframes: {
        pulse: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%':       { opacity: '.5', transform: 'scale(1.35)' },
        },
        fadeSlide: {
          from: { opacity: '0', transform: 'translateY(-5px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        spin: { to: { transform: 'rotate(360deg)' } },
      },
      animation: {
        pulse:     'pulse 2s infinite',
        fadeSlide: 'fadeSlide 0.22s ease both',
        spin:      'spin 1s linear infinite',
      },
    },
  },
  plugins: [],
}
