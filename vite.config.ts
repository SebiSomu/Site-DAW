import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vitest/config'

const backendUrl = process.env.BACKEND_URL ?? 'http://127.0.0.1:5000'

export default defineConfig({
  plugins: [svelte()],
  test: {
    include: ['src/**/*.test.ts'],
  },
  server: {
    proxy: {
      '/api': { target: backendUrl, changeOrigin: false },
      '/uploads': { target: backendUrl, changeOrigin: false },
      '/robots.txt': { target: backendUrl, changeOrigin: false },
      '/sitemap.xml': { target: backendUrl, changeOrigin: false },
    },
  },
})
