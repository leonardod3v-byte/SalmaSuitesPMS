/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        hotel: {
          bg: '#1A0F0A',
          surface: '#2D1B14',
          hover: '#3D261C',
          border: '#4A352C',
          text: {
            primary: '#F2EFE9',
            secondary: '#BDB2A7',
            tertiary: '#827066',
          },
          gold: {
            DEFAULT: '#B38E5D',
            light: '#D9C5A3',
            dark: '#735C3D',
          },
          success: '#2D6A4F',
          error: '#9B2226',
          info: '#1E3A5F',
          vip: '#582F7E',
        }
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        ui: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'hotel-sm': '0 2px 8px rgba(0, 0, 0, 0.4)',
        'hotel-md': '0 6px 20px rgba(0, 0, 0, 0.5)',
        'hotel-lg': '0 16px 40px rgba(0, 0, 0, 0.6)',
        'hotel-gold': '0 0 24px rgba(179, 142, 93, 0.2)',
      },
      borderRadius: {
        hotel: '0.5rem',
      },
      transitionTimingFunction: {
        hotel: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    }
  },
  plugins: []
};