<script lang="ts">
  import type { AdminSummary } from '../../lib/api/admin-types'
  import { api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatDate, formatPrice } from '../../lib/format'
  import { auth } from '../../lib/stores/auth.svelte'

  let summary = $state<AdminSummary | null>(null)
  let error = $state('')

  const isAdmin = $derived(auth.user?.role === 'admin')

  $effect(() => {
    if (!isAdmin) return
    api
      .get<AdminSummary>('/admin/summary')
      .then((body) => (summary = body))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })
</script>

<Seo title="Admin dashboard" description="How the shop is doing today." noindex />

<AdminGate>
  <section class="page-stack">
    <h1 class="page-title">Dashboard</h1>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if !summary}
      <p class="status" aria-live="polite">Adding up the order book…</p>
    {:else}
      <ul class="tiles">
        <li class="paper tile">
          <span class="tile-value">{formatPrice(summary.revenue_cents)}</span>
          <span class="tile-label">taken from {summary.paid_orders} paid {summary.paid_orders === 1 ? 'order' : 'orders'}</span>
        </li>
        <li class="paper tile">
          <a class="tile-value" href="/admin/orders?status=paid">{summary.orders_to_send}</a>
          <span class="tile-label">{summary.orders_to_send === 1 ? 'order' : 'orders'} to wrap and send</span>
        </li>
        <li class="paper tile">
          <a class="tile-value" href="/admin/orders?status=pending_payment">{summary.awaiting_payment}</a>
          <span class="tile-label">awaiting payment</span>
        </li>
        <li class="paper tile">
          <a class="tile-value" href="/admin/messages">{summary.messages}</a>
          <span class="tile-label">{summary.messages === 1 ? 'message' : 'messages'} from visitors</span>
        </li>
      </ul>

      <div class="dashboard-columns">
        <div class="paper table-scroll">
          <table class="data-table">
            <caption>Orders by status</caption>
            <thead>
              <tr>
                <th scope="col">Status</th>
                <th scope="col" class="number">Orders</th>
              </tr>
            </thead>
            <tbody>
              {#each summary.orders_by_status as row (row.code)}
                <tr>
                  <th scope="row">
                    <a href={`/admin/orders?status=${row.code}`}>
                      <span class="order-status" data-status={row.code}>{row.name}</span>
                    </a>
                  </th>
                  <td class="number">{row.count}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <div class="paper table-scroll">
          <table class="data-table">
            <caption>Running low</caption>
            <thead>
              <tr>
                <th scope="col">Jar</th>
                <th scope="col" class="number">Left</th>
                <th scope="col">In the shop</th>
              </tr>
            </thead>
            <tbody>
              {#each summary.low_stock as jar (jar.id)}
                <tr>
                  <th scope="row"><a href={`/admin/products/${jar.id}`}>{jar.name}</a></th>
                  <td class="number">{jar.stock === 0 ? 'Sold out' : jar.stock}</td>
                  <td>{jar.is_active ? 'Shown' : 'Hidden'}</td>
                </tr>
              {:else}
                <tr><td colspan="3">Every jar has more than 5 left.</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

      <div class="paper table-scroll">
        <table class="data-table">
          <caption>Newest orders</caption>
          <thead>
            <tr>
              <th scope="col">Order</th>
              <th scope="col">Date</th>
              <th scope="col">Customer</th>
              <th scope="col">Status</th>
              <th scope="col" class="number">Total</th>
            </tr>
          </thead>
          <tbody>
            {#each summary.recent_orders as order (order.id)}
              <tr>
                <th scope="row"><a href={`/admin/orders/${order.id}`}>Order {order.id}</a></th>
                <td><time datetime={order.created_at}>{formatDate(order.created_at)}</time></td>
                <td>{order.customer.name}</td>
                <td><span class="order-status" data-status={order.status.code}>{order.status.name}</span></td>
                <td class="number">{formatPrice(order.total_cents)}</td>
              </tr>
            {:else}
              <tr><td colspan="5">No orders yet.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </section>
</AdminGate>

<style>
  .tiles {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
    gap: var(--space-md);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .tile {
    display: grid;
    gap: var(--space-2xs);
    padding: var(--space-md) var(--space-lg);
  }

  .tile-value {
    font-family: var(--font-label);
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--color-jam);
  }

  .tile-label {
    color: var(--color-ink-soft);
  }

  .dashboard-columns {
    display: grid;
    gap: var(--space-lg);
    align-items: start;
  }

  .dashboard-columns .data-table {
    min-width: 0;
  }

  @media (min-width: 1024px) {
    .dashboard-columns {
      grid-template-columns: 1fr 1fr;
    }
  }
</style>
