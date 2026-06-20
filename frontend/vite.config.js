import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8002',
      '/v1': 'http://localhost:8002',
      '/chat': 'http://localhost:8002',
      '/health': 'http://localhost:8002',
    },
  },
});
