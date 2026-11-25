<script lang="ts">
  import type { Snippet } from 'svelte'
  import { auth } from '../stores/auth.svelte'
  import AdminNav from './AdminNav.svelte'
  import AuthGate from './AuthGate.svelte'

  let { children }: { children: Snippet } = $props()
</script>

<AuthGate>
  {#if auth.user?.role === 'admin'}
    <div class="admin-shell">
      <AdminNav />
      {@render children()}
    </div>
  {:else}
    <section class="page-stack narrow">
      <h1 class="page-title">Only for the kitchen</h1>
      <p class="status">This part of the shop is for Mama and the people who help her run it.</p>
      <p><a class="button" href="/">Back to the shop</a></p>
    </section>
  {/if}
</AuthGate>

<style>
  .admin-shell {
    display: grid;
    gap: var(--space-xl);
  }
</style>
