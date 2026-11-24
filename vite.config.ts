import { readFileSync } from 'node:fs'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vitest/config'

interface HeaderPolicy {
  common: Record<string, string>
  site_csp: string[]
}

const backendUrl = process.env.BACKEND_URL ?? 'http://127.0.0.1:5000'
const policy: HeaderPolicy = JSON.parse(readFileSync(new URL('./security-headers.json', import.meta.url), 'utf-8'))
const devOnlySources: Record<string, string> = {
  'style-src': "'unsafe-inline'",
  'connect-src': 'ws://localhost:* ws://127.0.0.1:*',
}

function withDevSources(directive: string): string {
  const name = directive.split(' ')[0]
  return name in devOnlySources ? `${directive} ${devOnlySources[name]}` : directive
}

function siteHeaders(directives: string[]): Record<string, string> {
  return { ...policy.common, 'Content-Security-Policy': directives.join('; ') }
}

const backendProxy = {
  '/api': { target: backendUrl, changeOrigin: false },
  '/uploads': { target: backendUrl, changeOrigin: false },
  '/robots.txt': { target: backendUrl, changeOrigin: false },
  '/sitemap.xml': { target: backendUrl, changeOrigin: false },
}

export default defineConfig({
  plugins: [svelte()],
  test: {
    include: ['src/**/*.test.ts'],
  },
  server: {
    headers: siteHeaders(policy.site_csp.map(withDevSources)),
    proxy: backendProxy,
  },
  preview: {
    headers: siteHeaders(policy.site_csp),
    proxy: backendProxy,
  },
})
