import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Traffic Light System
        risk: {
          high: '#EF4444',      // Red - Riesgo de cierre/despidos
          medium: '#F59E0B',    // Amber
          low: '#10B981'        // Green - Alta probabilidad
        },
        opportunity: {
          funding: '#F59E0B',   // Golden - Funding inminente
          hiring: '#10B981',    // Green - Alta contratación
          stable: '#3B82F6',    // Blue - Estable
          declining: '#EF4444'  // Red - Declinando
        },
        brand: {
          primary: '#6366F1',   // Indigo
          secondary: '#8B5CF6', // Purple
          accent: '#EC4899'     // Pink
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

export default config
