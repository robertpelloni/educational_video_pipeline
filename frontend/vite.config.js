import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Inject Basic Auth headers for local dev environment
            // This assumes the backend uses admin:supersecretpipeline locally.
            const authStr = Buffer.from('admin:supersecretpipeline').toString('base64');
            proxyReq.setHeader('Authorization', `Basic ${authStr}`);
          });
        }
      },
    },
  },
})
