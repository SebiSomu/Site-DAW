export const CAPTCHA_HEADER = 'X-Captcha-Token'
export const TURNSTILE_SCRIPT_URL = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
export const CAPTCHA_LOAD_FAILED = 'The security check could not load. Check your connection and refresh the page.'
export const CAPTCHA_EXPIRED = 'The security check expired. Please tick it again.'

export interface TurnstileOptions {
  sitekey: string
  callback: (token: string) => void
  'expired-callback': () => void
  'error-callback': () => void
  theme: 'light' | 'dark' | 'auto'
  size: 'normal' | 'flexible' | 'compact'
}

export interface TurnstileApi {
  render(container: HTMLElement, options: TurnstileOptions): string
  reset(widgetId: string): void
  remove(widgetId: string): void
}

export interface ScriptHost {
  createElement(tag: 'script'): HTMLScriptElement
  head: { appendChild(node: HTMLScriptElement): unknown }
}

export interface TurnstileWindow {
  turnstile?: TurnstileApi
}

export function captchaHeaders(token: string): Record<string, string> {
  return { [CAPTCHA_HEADER]: token }
}

export function createTurnstileLoader(host: ScriptHost, scope: TurnstileWindow) {
  let loading: Promise<TurnstileApi> | null = null

  return function load(): Promise<TurnstileApi> {
    if (scope.turnstile) return Promise.resolve(scope.turnstile)
    loading ??= new Promise<TurnstileApi>((resolve, reject) => {
      const script = host.createElement('script')
      script.src = TURNSTILE_SCRIPT_URL
      script.async = true
      script.defer = true
      script.onload = () => (scope.turnstile ? resolve(scope.turnstile) : reject(new Error(CAPTCHA_LOAD_FAILED)))
      script.onerror = () => reject(new Error(CAPTCHA_LOAD_FAILED))
      host.head.appendChild(script)
    }).catch((error: unknown) => {
      loading = null
      throw error
    })
    return loading
  }
}
