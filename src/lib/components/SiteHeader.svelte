<script lang="ts">
  import { currentState, mainNavLinks } from '../navigation'
  import { router } from '../router/router.svelte'
  import { auth } from '../stores/auth.svelte'
  import { cart } from '../stores/cart.svelte'

  let open = $state(false)

  const here = $derived(router.url.pathname + router.url.search)
  const links = $derived(mainNavLinks(auth.user !== null))

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
    <a class="cart-link" href="/cart" aria-current={here === '/cart' ? 'page' : undefined}>
      {#key cart.count}
        <svg class:lid-pop={cart.count > 0} viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
          <path class="cart-lid" d="M5 4h14a1 1 0 0 1 1 1v3H4V5a1 1 0 0 1 1-1z" />
          <path class="cart-jar" d="M6 8h12v11a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z" />
        </svg>
      {/key}
      <span class="cart-word">Cart</span>
      <span class="cart-count">{cart.count}</span>
      <span class="visually-hidden">{cart.count === 1 ? 'jar' : 'jars'}</span>
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
          <li><a href={link.href} aria-current={currentState(link.href, router.url.pathname)}>{link.label}</a></li>
        {/each}
      </ul>
    </nav>
  </div>
</header>
