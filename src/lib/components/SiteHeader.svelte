<script lang="ts">
  import { router } from '../router/router.svelte'
  import { SHELVES, shelfHref } from '../shelves'

  let open = $state(false)

  const here = $derived(router.url.pathname + router.url.search)
  const links = [{ href: '/products', label: 'All jars' }, ...SHELVES.map((shelf) => ({ href: shelfHref(shelf.slug), label: shelf.name }))]

  $effect(() => {
    void here
    open = false
  })
</script>

<header class="site-header">
  <div class="gingham" aria-hidden="true"></div>
  <div class="header-bar page-width">
    <a class="brand" href="/">
      <svg class="brand-lid" viewBox="0 0 80 80" width="64" height="64" aria-hidden="true">
        <defs>
          <pattern id="brand-gingham" width="9" height="9" patternUnits="userSpaceOnUse">
            <rect class="cloth-ground" width="9" height="9" />
            <rect class="cloth-check" width="4.5" height="9" />
            <rect class="cloth-check" width="9" height="4.5" />
          </pattern>
        </defs>
        <path
          class="lid-cloth"
          d="M74.0 40.0A6.2 6.2 0 0 1 72.3 50.5A6.2 6.2 0 0 1 67.5 60.0A6.2 6.2 0 0 1 60.0 67.5A6.2 6.2 0 0 1 50.5 72.3A6.2 6.2 0 0 1 40.0 74.0A6.2 6.2 0 0 1 29.5 72.3A6.2 6.2 0 0 1 20.0 67.5A6.2 6.2 0 0 1 12.5 60.0A6.2 6.2 0 0 1 7.7 50.5A6.2 6.2 0 0 1 6.0 40.0A6.2 6.2 0 0 1 7.7 29.5A6.2 6.2 0 0 1 12.5 20.0A6.2 6.2 0 0 1 20.0 12.5A6.2 6.2 0 0 1 29.5 7.7A6.2 6.2 0 0 1 40.0 6.0A6.2 6.2 0 0 1 50.5 7.7A6.2 6.2 0 0 1 60.0 12.5A6.2 6.2 0 0 1 67.5 20.0A6.2 6.2 0 0 1 72.3 29.5A6.2 6.2 0 0 1 74.0 40.0Z"
        />
        <circle class="lid-twine" cx="40" cy="40" r="26" />
        <path class="lid-bow" d="M62 30c7-6 13-2 9 4M62 30c5-8 0-12-5-7" />
        <circle class="lid-label" cx="40" cy="40" r="19" />
        <text class="lid-text" x="40" y="46" text-anchor="middle">Mum's</text>
      </svg>
      <span class="brand-words">
        <span class="brand-top">Mum's</span>
        <span class="brand-name">Homemade<br />Jams</span>
      </span>
    </a>
    <button
      class="button button-quiet menu-toggle"
      type="button"
      aria-expanded={open}
      aria-controls="site-nav"
      onclick={() => (open = !open)}
    >
      Menu
    </button>
    <nav id="site-nav" class="site-nav" aria-label="Main" data-open={open}>
      <ul>
        {#each links as link (link.href)}
          <li><a href={link.href} aria-current={here === link.href ? 'page' : undefined}>{link.label}</a></li>
        {/each}
      </ul>
    </nav>
  </div>
</header>
