<script lang="ts">
  import SiteFooter from './lib/components/SiteFooter.svelte'
  import SiteHeader from './lib/components/SiteHeader.svelte'
  import { router } from './lib/router/router.svelte'
  import { auth } from './lib/stores/auth.svelte'
  import AboutPage from './pages/AboutPage.svelte'
  import AccountPage from './pages/AccountPage.svelte'
  import CartPage from './pages/CartPage.svelte'
  import CheckoutCancelledPage from './pages/CheckoutCancelledPage.svelte'
  import CheckoutPage from './pages/CheckoutPage.svelte'
  import CheckoutSuccessPage from './pages/CheckoutSuccessPage.svelte'
  import HomePage from './pages/HomePage.svelte'
  import LoginPage from './pages/LoginPage.svelte'
  import NotFoundPage from './pages/NotFoundPage.svelte'
  import OrderPage from './pages/OrderPage.svelte'
  import OrdersPage from './pages/OrdersPage.svelte'
  import ProductPage from './pages/ProductPage.svelte'
  import ProductsPage from './pages/ProductsPage.svelte'
  import RegisterPage from './pages/RegisterPage.svelte'

  const path = $derived(router.url.pathname)
  const productSlug = $derived(path.match(/^\/products\/([^/]+)$/)?.[1])
  const orderId = $derived(path.match(/^\/account\/orders\/([1-9][0-9]*)$/)?.[1])

  auth.load()
</script>

<a class="skip-link" href="#main">Skip to content</a>
<SiteHeader />

<main id="main" class="site-main page-width" tabindex="-1">
  {#if path === '/'}
    <HomePage />
  {:else if path === '/about'}
    <AboutPage />
  {:else if path === '/products'}
    <ProductsPage />
  {:else if productSlug}
    {#key productSlug}
      <ProductPage slug={productSlug} />
    {/key}
  {:else if path === '/cart'}
    <CartPage />
  {:else if path === '/checkout'}
    <CheckoutPage />
  {:else if path === '/checkout/success'}
    <CheckoutSuccessPage />
  {:else if path === '/checkout/cancelled'}
    <CheckoutCancelledPage />
  {:else if path === '/login'}
    <LoginPage />
  {:else if path === '/register'}
    <RegisterPage />
  {:else if path === '/account'}
    <AccountPage />
  {:else if path === '/account/orders'}
    <OrdersPage />
  {:else if orderId}
    {#key orderId}
      <OrderPage id={orderId} />
    {/key}
  {:else}
    <NotFoundPage />
  {/if}
</main>

<SiteFooter />
