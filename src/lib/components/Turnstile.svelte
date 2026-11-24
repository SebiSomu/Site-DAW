<script lang="ts" module>
  import { api } from '../api/client'
  import { createTurnstileLoader, type TurnstileWindow } from '../captcha'

  let siteKey: Promise<string> | null = null

  function loadSiteKey(): Promise<string> {
    siteKey ??= api
      .get<{ site_key: string }>('/captcha')
      .then((body) => body.site_key)
      .catch((error: unknown) => {
        siteKey = null
        throw error
      })
    return siteKey
  }

  const loadTurnstile = createTurnstileLoader(document, window as TurnstileWindow)
</script>

<script lang="ts">
  import { onMount } from 'svelte'
  import { CAPTCHA_EXPIRED, CAPTCHA_LOAD_FAILED, type TurnstileApi } from '../captcha'

  let { token = $bindable('') }: { token?: string } = $props()

  let container: HTMLDivElement
  let problem = $state('')
  let turnstile: TurnstileApi | null = null
  let widgetId: string | null = null

  export function reset(): void {
    token = ''
    if (turnstile && widgetId !== null) turnstile.reset(widgetId)
  }

  onMount(() => {
    let destroyed = false
    Promise.all([loadSiteKey(), loadTurnstile()])
      .then(([sitekey, loaded]) => {
        if (destroyed) return
        turnstile = loaded
        widgetId = loaded.render(container, {
          sitekey,
          theme: 'light',
          size: 'flexible',
          callback: (value) => {
            token = value
            problem = ''
          },
          'expired-callback': () => {
            token = ''
            problem = CAPTCHA_EXPIRED
          },
          'error-callback': () => {
            token = ''
            problem = CAPTCHA_LOAD_FAILED
          },
        })
      })
      .catch(() => {
        problem = CAPTCHA_LOAD_FAILED
      })
    return () => {
      destroyed = true
      if (turnstile && widgetId !== null) turnstile.remove(widgetId)
    }
  })
</script>

<div class="captcha field-wide" role="group" aria-label="Security check">
  <div bind:this={container}></div>
  {#if problem}
    <p class="form-error" role="alert">{problem}</p>
  {/if}
</div>

<style>
  .captcha {
    display: grid;
    gap: var(--space-2xs);
    min-height: 65px;
  }
</style>
