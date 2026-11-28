import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    build: {
      // The only chunk over Vite's 500 KB default is the landing page's three.js
      // scene (~530 KB, 131 KB gzip), which is lazy-loaded after first paint and
      // never inside the app. Any other chunk growing this large still warns.
      chunkSizeWarningLimit: 560,
    },
    server: {
      port: 5174,
      strictPort: true,
      // Forward API calls to Django so the browser sees one origin.
      proxy: {
        '/api': {
          target: env.VITE_DEV_API_TARGET || 'http://127.0.0.1:8000',
          changeOrigin: false,
        },
      },
    },
  }
})
