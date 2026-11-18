<script lang="ts">
  import { ADMIN_LINKS } from '../admin'
  import { currentState } from '../navigation'
  import { router } from '../router/router.svelte'

  function state(href: string): 'page' | 'true' | undefined {
    const pathname = router.url.pathname
    if (href === '/admin') return pathname === href ? 'page' : undefined
    return currentState(href, pathname)
  }
</script>

<nav class="admin-nav" aria-label="Admin">
  <ul>
    {#each ADMIN_LINKS as link (link.href)}
      <li><a href={link.href} aria-current={state(link.href)}>{link.label}</a></li>
    {/each}
  </ul>
</nav>

<style>
  .admin-nav ul {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-xs);
    margin: 0;
    padding: var(--space-xs);
    list-style: none;
    background: var(--color-paper-shade);
    border-radius: var(--radius-paper);
  }

  .admin-nav a {
    display: inline-flex;
    align-items: center;
    min-height: 2.75rem;
    padding: 0 var(--space-md);
    border-radius: var(--radius-pill);
    font-weight: 700;
    color: var(--color-ink);
    text-decoration: none;
  }

  .admin-nav a:hover {
    background: var(--color-paper);
  }

  .admin-nav a[aria-current] {
    background: var(--color-jam);
    color: var(--color-paper);
  }
</style>
