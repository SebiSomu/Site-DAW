<script lang="ts">
  import { errorMessage } from '../lib/api/client'
  import Seo from '../lib/components/Seo.svelte'
  import { loginHref, safeNextPath } from '../lib/redirects'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  let first_name = $state('')
  let last_name = $state('')
  let email = $state('')
  let phone = $state('')
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
      await auth.register({ first_name, last_name, email, password, phone: phone.trim() || undefined })
    } catch (caught) {
      error = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<Seo title="Create an account" description="Create an account to order Mum's homemade jams and follow your orders." noindex />

<section class="page-stack narrow">
  <h1 class="page-title">Create an account</h1>
  <form class="paper sheet form-grid" onsubmit={submit}>
    <label class="field">
      First name
      <input required maxlength="80" autocomplete="given-name" bind:value={first_name} />
    </label>
    <label class="field">
      Last name
      <input required maxlength="80" autocomplete="family-name" bind:value={last_name} />
    </label>
    <label class="field field-wide">
      Email
      <input type="email" required maxlength="255" autocomplete="email" bind:value={email} />
    </label>
    <label class="field field-wide">
      <span>Phone <span class="field-hint">(optional)</span></span>
      <input type="tel" maxlength="20" autocomplete="tel" bind:value={phone} />
    </label>
    <label class="field field-wide">
      <span>Password <span class="field-hint">(at least 8 characters)</span></span>
      <input type="password" required minlength="8" maxlength="128" autocomplete="new-password" bind:value={password} />
    </label>
    {#if error}
      <p class="form-error field-wide" role="alert">{error}</p>
    {/if}
    <p class="field-wide"><button class="button" type="submit" disabled={busy}>Create my account</button></p>
  </form>
  <p>Already have an account? <a href={loginHref(next)}>Log in</a></p>
</section>
