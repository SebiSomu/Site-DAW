<script lang="ts">
  import { hrefWithQuery, ORDER_STATUSES } from '../../lib/admin'
  import type { AdminOrderSummary } from '../../lib/api/admin-types'
  import { api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatDate, formatPrice } from '../../lib/format'
  import { router } from '../../lib/router/router.svelte'
  import { auth } from '../../lib/stores/auth.svelte'

  let orders = $state<AdminOrderSummary[] | null>(null)
  let error = $state('')

  const isAdmin = $derived(auth.user?.role === 'admin')
  const status = $derived(
    ORDER_STATUSES.find((option) => option.code === router.url.searchParams.get('status'))?.code ?? '',
  )

  $effect(() => {
    if (!isAdmin) return
    const filter = status
    orders = null
    error = ''
    api
      .get<{ orders: AdminOrderSummary[] }>('/admin/orders', { status: filter || undefined })
      .then((body) => (orders = body.orders))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  function filterBy(event: Event): void {
    const code = (event.currentTarget as HTMLSelectElement).value
    router.navigate(hrefWithQuery('/admin/orders', { status: code }))
  }
</script>

<Seo title="Orders" description="Every order placed in the shop." noindex />

<AdminGate>
  <section class="page-stack">
    <h1 class="page-title">Orders</h1>
    <label class="field status-filter">
      Show
      <select value={status} onchange={filterBy}>
        <option value="">Every order</option>
        {#each ORDER_STATUSES as option (option.code)}
          <option value={option.code}>{option.name}</option>
        {/each}
      </select>
    </label>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if !orders}
      <p class="status" aria-live="polite">Looking through the order book…</p>
    {:else}
      <div class="paper table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Order</th>
              <th scope="col">Date</th>
              <th scope="col">Customer</th>
              <th scope="col" class="number">Jars</th>
              <th scope="col" class="number">Total</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {#each orders as order (order.id)}
              <tr>
                <th scope="row"><a href={`/admin/orders/${order.id}`}>Order {order.id}</a></th>
                <td><time datetime={order.created_at}>{formatDate(order.created_at)}</time></td>
                <td>
                  {order.customer.name}
                  <span class="field-hint email">{order.customer.email}</span>
                </td>
                <td class="number">{order.jar_count}</td>
                <td class="number">{formatPrice(order.total_cents)}</td>
                <td><span class="order-status" data-status={order.status.code}>{order.status.name}</span></td>
              </tr>
            {:else}
              <tr><td colspan="6">No orders here.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </section>
</AdminGate>

<style>
  .status-filter {
    max-width: 18rem;
  }

  .email {
    display: block;
    font-size: var(--text-sm);
  }
</style>
