/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: {
    files: [
      "./src/**/*.{js,jsx,ts,tsx}",
    ],
  },
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        brand: {
          primary: '#0F4F99',
          primaryHover: '#0C74EE',
          primarySoft: '#489CFF',
          accent: '#E8F4FF',
        },
        line: {
          soft: '#E5E7EB',
          strong: '#D1D5DB',
        },
        // Enhanced gray scale
        gray: {
          50: '#F7F9FC',
          600: '#6B7280',
          800: '#1F2937',
          900: '#0B1220',
        }
      },
      fontFamily: {
        sans: [
          'Pretendard', 'Inter', 'Noto Sans KR', 'system-ui', '-apple-system',
          'Segoe UI', 'Roboto', 'Apple SD Gothic Neo', 'Malgun Gothic', 'sans-serif'
        ],
      },
      fontSize: {
        'display': ['48px', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'h1': ['40px', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        'h2': ['32px', { lineHeight: '1.3', letterSpacing: '-0.01em' }],
        'h3': ['24px', { lineHeight: '1.4' }],
        'body': ['16px', { lineHeight: '1.6' }],
        'caption': ['14px', { lineHeight: '1.5' }],
        'label': ['12px', { lineHeight: '1.4' }],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        'custom-sm': '6px',
        'custom-md': '10px',
        'custom-lg': '14px',
        'custom-xl': '20px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0,0,0,0.06)',
        'md': '0 6px 16px rgba(0,0,0,0.08)',
        'lg': '0 12px 32px rgba(0,0,0,0.12)',
        'xl': '0 20px 40px rgba(0,0,0,0.15)',
      },
      maxWidth: {
        'container': '1200px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      backgroundImage: {
        'grid-pattern': 'radial-gradient(circle, rgba(0,0,0,0.1) 1px, transparent 1px)',
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      backgroundSize: {
        'grid': '20px 20px',
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
  ],
}
