<script lang="ts">
  import type { Snippet } from 'svelte'
  import { loginHref } from '../redirects'
  import { router } from '../router/router.svelte'
  import { auth } from '../stores/auth.svelte'

  let { children }: { children: Snippet } = $props()

  $effect(() => {
    if (auth.ready && !auth.user) router.replace(loginHref(router.url.pathname + router.url.search))
  })
</script>

{#if auth.user}
  {@render children()}
{:else}
  <p class="status" aria-live="polite">Checking who is at the door…</p>
{/if}
