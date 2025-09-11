const { colors } = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#0E5AE5',
          primaryHover: '#0B4BC2',
          primarySoft: '#E8F0FF',
        },
        line: {
          soft: '#E5E7EB',
          strong: '#D1D5DB',
        },
        // ui.json의 text 및 bg 색상을 Tailwind 기본 색상으로 확장
        gray: {
          ...colors.gray,
          50: '#F7F9FC', // bg.subtle
          600: '#6B7280', // text.muted
          800: '#1F2937', // text.base
          900: '#0B1220', // text.strong
        }
      },
      fontFamily: {
        sans: [
          'Pretendard', 'Inter', 'Noto Sans KR', 'system-ui', '-apple-system', 
          'Segoe UI', 'Roboto', 'Apple SD Gothic Neo', 'Malgun Gothic', 'sans-serif'
        ],
      },
      fontSize: {
        'display': '48px',
        'h1': '40px',
        'h2': '32px',
        'h3': '24px',
        'body': '16px',
        'caption': '14px',
        'label': '12px',
      },
      borderRadius: {
        'sm': '6px',
        'md': '10px',
        'lg': '14px',
        'xl': '20px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0,0,0,0.06)',
        'md': '0 6px 16px rgba(0,0,0,0.08)',
        'lg': '0 12px 32px rgba(0,0,0,0.12)',
      },
      maxWidth: {
        'container': '1200px',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
