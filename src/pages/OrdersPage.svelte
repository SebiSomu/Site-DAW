<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { OrderSummary } from '../lib/api/types'
  import AuthGate from '../lib/components/AuthGate.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatDate, formatPrice } from '../lib/format'
  import { auth } from '../lib/stores/auth.svelte'

  let orders = $state<OrderSummary[] | null>(null)
  let error = $state('')

  const signedIn = $derived(!!auth.user)

  $effect(() => {
    if (!signedIn) return
    api
      .get<{ orders: OrderSummary[] }>('/orders')
      .then((body) => (orders = body.orders))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })
</script>

<Seo title="My orders" description="Every order you have placed with Mum's Homemade Jams." noindex />

<AuthGate>
  <section class="page-stack">
    <h1 class="page-title">My orders</h1>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if orders === null}
      <p class="status" aria-live="polite">Looking through the order book…</p>
    {:else if orders.length}
      <div class="paper table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Order</th>
              <th scope="col">Date</th>
              <th scope="col">Jars</th>
              <th scope="col">Status</th>
              <th scope="col" class="number">Total</th>
            </tr>
          </thead>
          <tbody>
            {#each orders as order (order.id)}
              <tr>
                <th scope="row"><a href={`/account/orders/${order.id}`}>Order {order.id}</a></th>
                <td><time datetime={order.created_at}>{formatDate(order.created_at)}</time></td>
                <td>{order.jar_count}</td>
                <td><span class="order-status" data-status={order.status.code}>{order.status.name}</span></td>
                <td class="number">{formatPrice(order.total_cents)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="status">You have not ordered anything yet.</p>
      <p><a class="button" href="/products">Browse all jars</a></p>
    {/if}
    <p><a href="/account">Back to my account</a></p>
  </section>
</AuthGate>
