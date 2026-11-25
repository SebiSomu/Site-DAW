<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import { captchaHeaders } from '../lib/captcha'
  import Seo from '../lib/components/Seo.svelte'
  import Turnstile from '../lib/components/Turnstile.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  let name = $state('')
  let email = $state('')
  let subject = $state('')
  let message = $state('')
  let busy = $state(false)
  let captchaToken = $state('')
  let captcha: Turnstile
  let error = $state('')
  let sent = $state(false)

  $effect(() => {
    if (!auth.user) return
    name ||= `${auth.user.first_name} ${auth.user.last_name}`
    email ||= auth.user.email
  })

  async function send(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    busy = true
    error = ''
    try {
      await api.post('/contact', { name, email, subject, message }, captchaHeaders(captchaToken))
      sent = true
      subject = ''
      message = ''
      captcha.reset()
    } catch (caught) {
      error = errorMessage(caught)
      captcha.reset()
    } finally {
      busy = false
    }
  }
</script>

<Seo
  title="Contact us"
  description="Write to Mama's Pantry in Brașov about an order, a big batch for a wedding or anything else."
/>

<section class="page-stack contact">
  <div class="contact-text">
    <h1 class="page-title">Write to us</h1>
    <p class="lede">
      A question about an order, a batch for a wedding or a christening, or just a recipe you want to share? Mama reads
      every message herself, usually in the evening, and answers within two days.
    </p>
  </div>

  <form class="paper sheet form-grid" onsubmit={send}>
    {#if sent}
      <p class="form-note field-wide" role="status">Thank you! Your message is on its way to Mama.</p>
    {/if}
    <label class="field">
      Your name
      <input required maxlength="120" autocomplete="name" bind:value={name} />
    </label>
    <label class="field">
      Your email
      <input type="email" required maxlength="255" autocomplete="email" bind:value={email} />
    </label>
    <label class="field field-wide">
      Subject
      <input required maxlength="150" bind:value={subject} />
    </label>
    <label class="field field-wide">
      Message
      <textarea required rows="6" maxlength="5000" bind:value={message}></textarea>
    </label>
    {#if error}
      <p class="form-error field-wide" role="alert">{error}</p>
    {/if}
    <Turnstile bind:this={captcha} bind:token={captchaToken} />
    <p class="field-wide"><button class="button" type="submit" disabled={busy || !captchaToken}>Send message</button></p>
  </form>
</section>

<style>
  .contact {
    align-items: start;
  }

  .contact-text {
    display: grid;
    gap: var(--space-md);
    max-width: 40rem;
  }

  .lede {
    font-size: var(--text-lg);
  }

  @media (min-width: 1024px) {
    .contact {
      grid-template-columns: 2fr 3fr;
    }
  }
</style>
