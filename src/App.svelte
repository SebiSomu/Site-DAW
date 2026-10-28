<script lang="ts">
  import { router } from './lib/router/router.svelte'
  import HomePage from './pages/HomePage.svelte'
  import NotFoundPage from './pages/NotFoundPage.svelte'
  import ProductPage from './pages/ProductPage.svelte'
  import ProductsPage from './pages/ProductsPage.svelte'

  const path = $derived(router.url.pathname)
  const productSlug = $derived(path.match(/^\/products\/([^/]+)$/)?.[1])
</script>

<header class="site-header">
  <a class="brand" href="/">Mum's Homemade Jams</a>
  <nav aria-label="Main">
    <a href="/products">Shop</a>
  </nav>
</header>

<main>
  {#if path === '/'}
    <HomePage />
  {:else if path === '/products'}
    <ProductsPage />
  {:else if productSlug}
    {#key productSlug}
      <ProductPage slug={productSlug} />
    {/key}
  {:else}
    <NotFoundPage />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    background: #fffaf3;
    color: #3b1f24;
    font-family: system-ui, sans-serif;
    line-height: 1.5;
  }

  :global(h1, h2, h3) {
    font-family: Georgia, serif;
  }

  .site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e6d5c8;
  }

  .site-header a {
    color: #8b2d3a;
  }

  .brand {
    font-family: Georgia, serif;
    font-size: 1.25rem;
    font-weight: 700;
    text-decoration: none;
  }

  main {
    max-width: 72rem;
    margin: 0 auto;
    padding: 1.5rem 1rem 3rem;
  }
</style>
