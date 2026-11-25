<script lang="ts">
  import { confirmation } from '../../lib/stores/confirm.svelte'
  import { stepLabel } from '../../lib/admin'
  import type { AdminOrderDetail } from '../../lib/api/admin-types'
  import { ApiError, api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatDateTime, formatPrice } from '../../lib/format'
  import { auth } from '../../lib/stores/auth.svelte'

  let { id }: { id: string } = $props()

  let order = $state<AdminOrderDetail | null>(null)
  let error = $state('')
  let missing = $state(false)
  let changeError = $state('')
  let busy = $state(false)

  const isAdmin = $derived(auth.user?.role === 'admin')
  const wasPaid = $derived(order?.payment_status === 'succeeded')

  $effect(() => {
    if (!isAdmin) return
    api
      .get<{ order: AdminOrderDetail }>(`/admin/orders/${id}`)
      .then((body) => (order = body.order))
      .catch((caught: unknown) => {
        missing = caught instanceof ApiError && caught.status === 404
        error = errorMessage(caught)
      })
  })

  function confirmCancel(current: AdminOrderDetail): Promise<boolean> {
    return confirmation.ask({
      title: `Cancel order ${current.id}?`,
      message: wasPaid
        ? `${formatPrice(current.total_cents)} will be refunded to the customer's card and the jars go back in stock.`
        : 'The customer has not paid, so nothing is refunded.',
      confirmLabel: 'Cancel the order',
      cancelLabel: 'Keep it',
    })
  }

  async function moveTo(code: string): Promise<void> {
    if (!order || (code === 'cancelled' && !(await confirmCancel(order)))) return
    busy = true
    changeError = ''
    try {
      order = (await api.patch<{ order: AdminOrderDetail }>(`/admin/orders/${id}/status`, { status: code })).order
    } catch (caught) {
      changeError = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<Seo title={`Order ${id}`} description="One order, its customer and what happens next." noindex />

<AdminGate>
  <section class="page-stack">
    <p><a href="/admin/orders">Back to all orders</a></p>
    {#if order}
      <h1 class="page-title">Order {order.id}</h1>
      <p>
        <span class="order-status" data-status={order.status.code}>{order.status.name}</span>
        placed on <time datetime={order.created_at}>{formatDateTime(order.created_at)}</time>
      </p>

      <div class="paper sheet">
        <h2>Next step</h2>
        {#if order.next_statuses.length}
          <p class="steps">
            {#each order.next_statuses as step (step.code)}
              <button
                class={step.code === 'cancelled' ? 'button button-quiet' : 'button'}
                type="button"
                disabled={busy}
                onclick={() => moveTo(step.code)}>{stepLabel(step.code, wasPaid)}</button
              >
            {/each}
          </p>
        {:else}
          <p>Nothing left to do for this order.</p>
        {/if}
        {#if order.status.code === 'pending_payment'}
          <p class="field-hint">Only Stripe can mark an order paid, once the money has arrived.</p>
        {/if}
        {#if changeError}
          <p class="form-error" role="alert">{changeError}</p>
        {/if}
      </div>

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
                <td>{item.product_name}</td>
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

      <div class="details">
        <div class="paper sheet">
          <h2>Customer</h2>
          <p>{order.customer.name}</p>
          <p><a href={`mailto:${order.customer.email}`}>{order.customer.email}</a></p>
          {#if order.customer.phone}
            <p><a href={`tel:${order.customer.phone.replaceAll(' ', '')}`}>{order.customer.phone}</a></p>
          {/if}
        </div>
        <div class="paper sheet">
          <h2>Going to</h2>
          <p>{order.ships_to}</p>
          {#if order.notes}
            <h2>Note for Mama</h2>
            <p class="note">{order.notes}</p>
          {/if}
        </div>
        <div class="paper sheet">
          <h2>Payment</h2>
          <p>{order.payment_status ? `Card payment ${order.payment_status}` : 'No payment started yet'}</p>
          {#if order.paid_at}
            <p>Paid on <time datetime={order.paid_at}>{formatDateTime(order.paid_at)}</time></p>
          {/if}
        </div>
      </div>
    {:else if error}
      <h1 class="page-title">{missing ? 'We could not find this order' : 'Something went wrong'}</h1>
      <p class="status status-error" role="alert">{error}</p>
    {:else}
      <p class="status" aria-live="polite">Looking through the order book…</p>
    {/if}
  </section>
</AdminGate>

<style>
  .steps {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-sm);
  }

  .details {
    display: grid;
    gap: var(--space-lg);
    align-items: start;
  }

  .note {
    white-space: pre-wrap;
  }

  @media (min-width: 1024px) {
    .details {
      grid-template-columns: repeat(3, 1fr);
    }
  }
</style>
