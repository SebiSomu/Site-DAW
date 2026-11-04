<script lang="ts">
  import { errorMessage } from '../lib/api/client'
  import Seo from '../lib/components/Seo.svelte'
  import { safeNextPath } from '../lib/redirects'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  let email = $state('')
  let password = $state('')
  let busy = $state(false)
  let error = $state('')

  const next = $derived(safeNextPath(router.url.searchParams.get('next')))

  $effect(() => {
    if (auth.user) router.replace(next)
  })

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    busy = true
    error = ''
    try {
      await auth.login({ email, password })
    } catch (caught) {
      error = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<Seo title="Log in" description="Log in to your account to check out and follow your orders of Mum's homemade jams." noindex />

<section class="page-stack narrow">
  <h1 class="page-title">Log in</h1>
  <form class="paper sheet" onsubmit={submit}>
    <label class="field">
      Email
      <input type="email" required maxlength="255" autocomplete="email" bind:value={email} />
    </label>
    <label class="field">
      Password
      <input type="password" required maxlength="128" autocomplete="current-password" bind:value={password} />
    </label>
    {#if error}
      <p class="form-error" role="alert">{error}</p>
    {/if}
    <p><button class="button" type="submit" disabled={busy}>Log in</button></p>
  </form>
  <p>New here? <a href={`/register?next=${encodeURIComponent(next)}`}>Create an account</a></p>
</section>
