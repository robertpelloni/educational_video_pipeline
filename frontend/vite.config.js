import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyAuthUsername = env.API_USERNAME || 'admin';
  const proxyAuthPassword = env.API_PASSWORD || 'supersecretpipeline';

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (proxyReq, _req, _res) => {
              // Inject Basic Auth headers for local dev environment
              const authStr = Buffer.from(`${proxyAuthUsername}:${proxyAuthPassword}`).toString('base64');
              proxyReq.setHeader('Authorization', `Basic ${authStr}`);
            });
          }
        },
      },
    },
  }
})
