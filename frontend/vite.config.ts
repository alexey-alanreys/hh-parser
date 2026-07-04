import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev-only: proxy /api to uvicorn to avoid CORS. nginx does this in prod.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
