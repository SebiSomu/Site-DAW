<script lang="ts">
  import { confirmation } from '../../lib/stores/confirm.svelte'
  import { hrefWithQuery, positiveInt } from '../../lib/admin'
  import type { MessagesPage } from '../../lib/api/admin-types'
  import { api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Pager from '../../lib/components/Pager.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatDateTime } from '../../lib/format'
  import { router } from '../../lib/router/router.svelte'
  import { auth } from '../../lib/stores/auth.svelte'

  let result = $state<MessagesPage | null>(null)
  let error = $state('')
  let deleteError = $state('')
  let busy = $state(false)
  let reloads = $state(0)

  const isAdmin = $derived(auth.user?.role === 'admin')
  const page = $derived(positiveInt(router.url.searchParams.get('page')) ?? 1)

  $effect(() => {
    if (!isAdmin) return
    void reloads
    const wanted = page
    error = ''
    api
      .get<MessagesPage>('/admin/messages', { page: wanted })
      .then((body) => (result = body))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  function replyHref(email: string, subject: string): string {
    return `mailto:${email}?subject=${encodeURIComponent(`Re: ${subject}`)}`
  }

  async function remove(id: number, subject: string): Promise<void> {
    const confirmed = await confirmation.ask({
      title: 'Delete this message?',
      message: `"${subject}" will be gone for good.`,
      confirmLabel: 'Delete',
    })
    if (!confirmed) return
    busy = true
    deleteError = ''
    try {
      await api.delete(`/admin/messages/${id}`)
      reloads += 1
    } catch (caught) {
      deleteError = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<Seo title="Messages" description="Messages sent through the contact form." noindex />

<AdminGate>
  <section class="page-stack">
    <h1 class="page-title">Messages</h1>
    {#if deleteError}
      <p class="form-error" role="alert">{deleteError}</p>
    {/if}
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if !result}
      <p class="status" aria-live="polite">Opening the post…</p>
    {:else if result.messages.length}
      <p class="field-hint">{result.total} {result.total === 1 ? 'message' : 'messages'}, newest first.</p>
      <ul class="messages">
        {#each result.messages as message (message.id)}
          <li>
            <article class="paper sheet" aria-labelledby={`message-${message.id}`}>
              <h2 id={`message-${message.id}`}>{message.subject}</h2>
              <p class="from">
                From {message.name},
                <a href={replyHref(message.email, message.subject)}>{message.email}</a>,
                <time datetime={message.created_at}>{formatDateTime(message.created_at)}</time>
              </p>
              <p class="body">{message.message}</p>
              <p class="actions">
                <a class="button" href={replyHref(message.email, message.subject)}>Reply by email</a>
                <button class="button button-quiet" type="button" disabled={busy} onclick={() => remove(message.id, message.subject)}>
                  Delete
                </button>
              </p>
            </article>
          </li>
        {/each}
      </ul>
      <Pager page={result.page} pages={result.pages} href={(number) => hrefWithQuery('/admin/messages', { page: number })} />
    {:else}
      <p class="status">No messages yet.</p>
    {/if}
  </section>
</AdminGate>

<style>
  .messages {
    display: grid;
    gap: var(--space-md);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .from {
    color: var(--color-ink-soft);
  }

  .body {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-sm);
  }
</style>
