<script lang="ts">
  import SiteFooter from './lib/components/SiteFooter.svelte'
  import SiteHeader from './lib/components/SiteHeader.svelte'
  import { router } from './lib/router/router.svelte'
  import HomePage from './pages/HomePage.svelte'
  import NotFoundPage from './pages/NotFoundPage.svelte'
  import ProductPage from './pages/ProductPage.svelte'
  import ProductsPage from './pages/ProductsPage.svelte'

  const path = $derived(router.url.pathname)
  const productSlug = $derived(path.match(/^\/products\/([^/]+)$/)?.[1])
</script>

<a class="skip-link" href="#main">Skip to content</a>
<SiteHeader />

<main id="main" class="site-main page-width" tabindex="-1">
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

<SiteFooter />
