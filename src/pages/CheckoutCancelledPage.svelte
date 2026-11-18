<script lang="ts">
  import Seo from '../lib/components/Seo.svelte'
  import { orderIdFrom } from '../lib/payment'
  import { router } from '../lib/router/router.svelte'

  const orderId = $derived(orderIdFrom(router.url.searchParams.get('order')))
</script>

<Seo title="Payment cancelled" description="You left the payment page before paying." noindex />

<section class="page-stack narrow">
  <h1 class="page-title">Payment cancelled</h1>
  <p class="form-note" role="status">Nothing was charged to your card.</p>
  {#if orderId}
    <p>
      Your order is saved and waiting for payment. Whenever you are ready, open it and choose "Pay now". The jars are not
      set aside until it is paid, so do not wait too long if one is nearly sold out.
    </p>
    <p class="actions">
      <a class="button" href={`/account/orders/${orderId}`}>Go to order {orderId}</a>
      <a href="/products">Back to all jars</a>
    </p>
  {:else}
    <p class="actions">
      <a class="button" href="/account/orders">See my orders</a>
      <a href="/products">Back to all jars</a>
    </p>
  {/if}
</section>

<style>
  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-md);
  }
</style>
