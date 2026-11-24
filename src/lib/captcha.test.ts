import { describe, expect, it, vi } from 'vitest'
import {
  CAPTCHA_LOAD_FAILED,
  TURNSTILE_SCRIPT_URL,
  captchaHeaders,
  createTurnstileLoader,
  type ScriptHost,
  type TurnstileApi,
  type TurnstileWindow,
} from './captcha'

const fakeApi: TurnstileApi = { render: vi.fn(() => 'widget-1'), reset: vi.fn(), remove: vi.fn() }

function fakeHost() {
  const scripts: HTMLScriptElement[] = []
  const host: ScriptHost = {
    createElement: () => ({}) as HTMLScriptElement,
    head: { appendChild: (node) => scripts.push(node) },
  }
  return { host, scripts }
}

describe('captcha', () => {
  it('sends the token in its own header', () => {
    expect(captchaHeaders('abc')).toEqual({ 'X-Captcha-Token': 'abc' })
  })

  it('adds the Turnstile script once, even for several widgets', async () => {
    const { host, scripts } = fakeHost()
    const scope: TurnstileWindow = {}
    const load = createTurnstileLoader(host, scope)

    const first = load()
    const second = load()
    scope.turnstile = fakeApi
    scripts[0].onload?.(new Event('load'))

    expect(scripts).toHaveLength(1)
    expect(scripts[0].src).toBe(TURNSTILE_SCRIPT_URL)
    expect(scripts[0].async).toBe(true)
    await expect(first).resolves.toBe(fakeApi)
    await expect(second).resolves.toBe(fakeApi)
  })

  it('uses Turnstile straight away when it is already on the page', async () => {
    const { host, scripts } = fakeHost()

    await expect(createTurnstileLoader(host, { turnstile: fakeApi })()).resolves.toBe(fakeApi)
    expect(scripts).toHaveLength(0)
  })

  it('reports a failed load and tries again next time', async () => {
    const { host, scripts } = fakeHost()
    const load = createTurnstileLoader(host, {})

    const failed = load()
    scripts[0].onerror?.(new Event('error'))
    await expect(failed).rejects.toThrow(CAPTCHA_LOAD_FAILED)

    load()
    expect(scripts).toHaveLength(2)
  })

  it('treats a script that loads without Turnstile as a failure', async () => {
    const { host, scripts } = fakeHost()
    const failed = createTurnstileLoader(host, {})()

    scripts[0].onload?.(new Event('load'))

    await expect(failed).rejects.toThrow(CAPTCHA_LOAD_FAILED)
  })
})
