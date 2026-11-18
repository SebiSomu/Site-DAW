<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { OrderDetail } from '../lib/api/types'
  import AuthGate from '../lib/components/AuthGate.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatPrice } from '../lib/format'
  import { orderIdFrom, waitForPayment, type PaymentOutcome } from '../lib/payment'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  let order = $state<OrderDetail | null>(null)
  let outcome = $state<PaymentOutcome | null>(null)
  let checking = $state(true)
  let error = $state('')
  let round = $state(0)

  const signedIn = $derived(!!auth.user)
  const orderId = $derived(orderIdFrom(router.url.searchParams.get('order')))
  const orderHref = $derived(`/account/orders/${orderId}`)

  $effect(() => {
    round
    if (!signedIn || !orderId) return
    const controller = new AbortController()
    checking = true
    error = ''
    waitForPayment(() => api.get<{ order: OrderDetail }>(`/orders/${orderId}`).then((body) => body.order), {
      signal: controller.signal,
    })
      .then((result) => {
        if (controller.signal.aborted || !result) return
        order = result.order
        outcome = result.outcome
      })
      .catch((caught: unknown) => {
        if (!controller.signal.aborted) error = errorMessage(caught)
      })
      .finally(() => {
        if (!controller.signal.aborted) checking = false
      })
    return () => controller.abort()
  })

  function checkAgain(): void {
    round += 1
  }
</script>

<Seo title="Thank you" description="The result of your card payment." noindex />

<AuthGate>
  <section class="page-stack narrow">
    {#if !orderId}
      <h1 class="page-title">We could not find this order</h1>
      <p>This link is missing its order number. Your orders are all in your account.</p>
      <p><a class="button" href="/account/orders">See my orders</a></p>
    {:else if checking && outcome !== 'pending'}
      <h1 class="page-title">One moment…</h1>
      <p class="status" aria-live="polite">Checking your payment with the bank.</p>
    {:else if error}
      <h1 class="page-title">Something went wrong</h1>
      <p class="status status-error" role="alert">{error}</p>
      <p><a href={orderHref}>Go to order {orderId}</a></p>
    {:else if outcome === 'paid' && order}
      <h1 class="page-title">Thank you!</h1>
      <div class="paper sheet" role="status">
        <p class="paid-stamp">Paid</p>
        <p>
          Your payment of <strong>{formatPrice(order.total_cents)}</strong> went through and Mum has your order. She will
          wrap {order.jar_count === 1 ? 'the jar in gingham and send it' : `the ${order.jar_count} jars in gingham and send them`}
          to {order.ships_to}.
        </p>
      </div>
      <p class="actions">
        <a class="button" href={orderHref}>See order {order.id}</a>
        <a href="/products">Keep browsing</a>
      </p>
    {:else if outcome === 'cancelled'}
      <h1 class="page-title">This order was cancelled</h1>
      <p class="form-note" role="status">
        A jar in it sold out while you were paying, so we cancelled the order. If your card was charged, the full amount
        is refunded automatically.
      </p>
      <p class="actions">
        <a class="button" href={orderHref}>See order {orderId}</a>
        <a href="/products">Back to all jars</a>
      </p>
    {:else}
      <h1 class="page-title">Almost there</h1>
      <p class="form-note" role="status">
        We are still confirming your payment. The bank can take a minute to tell us, so do not pay again. Your order page
        will show "Paid" as soon as it is through.
      </p>
      <p class="actions">
        <button class="button" type="button" disabled={checking} onclick={checkAgain}>
          {checking ? 'Checking…' : 'Check again'}
        </button>
        <a href={orderHref}>Go to order {orderId}</a>
      </p>
    {/if}
  </section>
</AuthGate>

<style>
  .paid-stamp {
    justify-self: start;
    padding: 0.1rem 0.9rem;
    border: 3px solid var(--color-jam);
    border-radius: 0.3rem;
    font-family: var(--font-hand);
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.2;
    color: var(--color-jam);
    rotate: -4deg;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-md);
  }
</style>
