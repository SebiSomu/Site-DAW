<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { Address, CartSummary, OrderDetail } from '../lib/api/types'
  import AddressForm from '../lib/components/AddressForm.svelte'
  import AuthGate from '../lib/components/AuthGate.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatPrice } from '../lib/format'
  import { startPayment } from '../lib/payment'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'
  import { cart } from '../lib/stores/cart.svelte'

  let summary = $state<CartSummary | null>(null)
  let addresses = $state<Address[]>([])
  let addressId = $state<number | null>(null)
  let notes = $state('')
  let error = $state('')
  let busy = $state(false)
  let leaving = $state(false)

  const signedIn = $derived(!!auth.user)
  const hasIssue = $derived(!!summary && (summary.missing_product_ids.length > 0 || summary.lines.some((line) => !line.is_available)))

  $effect(() => {
    if (!signedIn) return
    api
      .get<{ addresses: Address[] }>('/addresses')
      .then((body) => {
        addresses = body.addresses
      })
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  $effect(() => {
    const items = cart.items.map((item) => ({ ...item }))
    if (!signedIn || !items.length) return
    api
      .post<CartSummary>('/cart/validate', { items })
      .then((body) => (summary = body))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  function addressSaved(address: Address): void {
    addresses = [address, ...addresses]
    addressId = address.id
  }

  async function placeOrder(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    busy = true
    error = ''
    let order: OrderDetail
    try {
      order = (await api.post<{ order: OrderDetail }>('/orders', { address_id: addressId, items: cart.items, notes })).order
    } catch (caught) {
      error = errorMessage(caught)
      busy = false
      return
    }
    leaving = true
    cart.clear()
    try {
      await startPayment(order.id)
    } catch {
      router.navigate(`/account/orders/${order.id}?payment=unavailable`)
    }
  }
</script>

<Seo title="Checkout" description="Choose where your jars should go and place your order." noindex />

<AuthGate>
  <section class="page-stack">
    <h1 class="page-title">Checkout</h1>

    {#if leaving}
      <p class="status" aria-live="polite">Your order is saved. Taking you to the secure payment page…</p>
    {:else if !cart.items.length}
      <p class="status">Your cart is empty, so there is nothing to check out yet.</p>
      <p><a class="button" href="/products">Browse all jars</a></p>
    {:else if hasIssue}
      <p class="form-error" role="alert">Some jars in your cart have changed. Please check your cart before ordering.</p>
      <p><a class="button" href="/cart">Back to your cart</a></p>
    {:else}
      <div class="two-columns">
        <section class="paper sheet" aria-labelledby="ship-to">
          <h2 id="ship-to">Where should the jars go?</h2>
          {#if addresses.length}
            <fieldset class="address-choices">
              <legend class="visually-hidden">Choose a delivery address</legend>
              {#each addresses as address (address.id)}
                <label class="address-choice">
                  <input type="radio" name="address" value={address.id} bind:group={addressId} />
                  {address.one_line}
                </label>
              {/each}
            </fieldset>
            {#if !addressId}
              <p class="field-hint">Pick one of your addresses to carry on.</p>
            {/if}
          {:else}
            <p>Add your delivery address to carry on.</p>
          {/if}
          <details open={!addresses.length}>
            <summary>Use a new address</summary>
            <AddressForm onsaved={addressSaved} />
          </details>
        </section>

        <form class="paper sheet" aria-labelledby="your-order" onsubmit={placeOrder}>
          <h2 id="your-order">Your order</h2>
          {#if summary}
            <ul class="order-lines">
              {#each summary.lines as line (line.product.id)}
                <li>
                  <span>{line.quantity} × {line.product.name}</span>
                  <span>{formatPrice(line.subtotal_cents)}</span>
                </li>
              {/each}
              <li class="order-total"><span>Total</span><span class="price">{formatPrice(summary.total_cents)}</span></li>
            </ul>
          {:else}
            <p class="status" aria-live="polite">Counting the jars…</p>
          {/if}
          <label class="field">
            <span>A note for Mum <span class="field-hint">(optional)</span></span>
            <textarea rows="3" maxlength="500" bind:value={notes}></textarea>
          </label>
          {#if error}
            <p class="form-error" role="alert">{error}</p>
          {/if}
          <p class="field-hint">
            You pay by card on Stripe's secure page. Your card details never pass through this site.
          </p>
          <p><button class="button" type="submit" disabled={busy || !summary || !addressId}>Place order and pay</button></p>
        </form>
      </div>
    {/if}
  </section>
</AuthGate>

<style>
  .address-choices {
    display: grid;
    gap: var(--space-xs);
    margin: 0;
    padding: 0;
    border: 0;
  }

  .address-choice {
    display: flex;
    align-items: center;
    gap: var(--space-xs);
    min-height: 2.75rem;
  }

  summary {
    min-height: 2.75rem;
    font-weight: 700;
    cursor: pointer;
  }

  .order-lines {
    display: grid;
    gap: var(--space-xs);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .order-lines li {
    display: flex;
    justify-content: space-between;
    gap: var(--space-md);
  }

  .order-total {
    padding-top: var(--space-xs);
    border-top: 1px dashed var(--color-kraft-deep);
    font-weight: 700;
  }
</style>
