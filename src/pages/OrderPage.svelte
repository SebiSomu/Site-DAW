<script lang="ts">
  import { ApiError, api, errorMessage } from '../lib/api/client'
  import type { OrderDetail } from '../lib/api/types'
  import AuthGate from '../lib/components/AuthGate.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatDate, formatPrice } from '../lib/format'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  const AWAITING_PAYMENT = 'pending_payment'

  let { id }: { id: string } = $props()

  let order = $state<OrderDetail | null>(null)
  let error = $state('')
  let missing = $state(false)
  let cancelError = $state('')
  let busy = $state(false)

  const signedIn = $derived(!!auth.user)
  const justPlaced = $derived(router.url.searchParams.has('placed'))

  $effect(() => {
    if (!signedIn) return
    api
      .get<{ order: OrderDetail }>(`/orders/${id}`)
      .then((body) => (order = body.order))
      .catch((caught: unknown) => {
        missing = caught instanceof ApiError && caught.status === 404
        error = errorMessage(caught)
      })
  })

  async function cancelOrder(): Promise<void> {
    if (!window.confirm(`Cancel order ${id}?`)) return
    busy = true
    cancelError = ''
    try {
      order = (await api.post<{ order: OrderDetail }>(`/orders/${id}/cancel`)).order
    } catch (caught) {
      cancelError = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<Seo title={`Order ${id}`} description="The jars in this order, where they are going and how far along it is." noindex />

<AuthGate>
  <section class="page-stack">
    {#if order}
      <h1 class="page-title">Order {order.id}</h1>
      {#if justPlaced}
        <p class="form-note" role="status">Thank you! Mum has your order.</p>
      {/if}
      {#if order.status.code === AWAITING_PAYMENT}
        <p class="form-note">Paying by card online is not switched on yet. This order is saved and waiting for payment.</p>
      {/if}
      <p>
        <span class="order-status" data-status={order.status.code}>{order.status.name}</span>
        placed on <time datetime={order.created_at}>{formatDate(order.created_at)}</time>
      </p>

      <div class="paper table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Jar</th>
              <th scope="col" class="number">Price</th>
              <th scope="col" class="number">Quantity</th>
              <th scope="col" class="number">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {#each order.items as item (item.product_slug)}
              <tr>
                <td><a href={`/products/${item.product_slug}`}>{item.product_name}</a></td>
                <td class="number">{formatPrice(item.unit_price_cents)}</td>
                <td class="number">{item.quantity}</td>
                <td class="number">{formatPrice(item.subtotal_cents)}</td>
              </tr>
            {/each}
          </tbody>
          <tfoot>
            <tr>
              <th scope="row" colspan="3">Total</th>
              <td class="number">{formatPrice(order.total_cents)}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="paper sheet">
        <h2>Going to</h2>
        <p>{order.ships_to}</p>
        {#if order.notes}
          <h2>Your note for Mum</h2>
          <p>{order.notes}</p>
        {/if}
      </div>

      {#if cancelError}
        <p class="form-error" role="alert">{cancelError}</p>
      {/if}
      {#if order.is_cancellable}
        <p><button class="button button-quiet" type="button" disabled={busy} onclick={cancelOrder}>Cancel this order</button></p>
      {/if}
    {:else if error}
      <h1 class="page-title">{missing ? 'We could not find this order' : 'Something went wrong'}</h1>
      <p class="status status-error" role="alert">{error}</p>
    {:else}
      <p class="status" aria-live="polite">Looking through the order book…</p>
    {/if}
    <p><a href="/account/orders">Back to my orders</a></p>
  </section>
</AuthGate>
