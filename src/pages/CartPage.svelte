<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { CartSummary } from '../lib/api/types'
  import QuantityPicker from '../lib/components/QuantityPicker.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatPrice } from '../lib/format'
  import { MAX_JARS_PER_LINE, cart } from '../lib/stores/cart.svelte'

  let summary = $state<CartSummary | null>(null)
  let error = $state('')
  let removedNote = $state(false)

  const canCheckOut = $derived(!!summary?.lines.length && summary.lines.every((line) => line.is_available))

  $effect(() => {
    const items = cart.items.map((item) => ({ ...item }))
    if (!items.length) {
      summary = null
      return
    }
    let active = true
    error = ''
    api
      .post<CartSummary>('/cart/validate', { items })
      .then((body) => {
        if (!active) return
        summary = body
        if (body.missing_product_ids.length) {
          removedNote = true
          cart.removeMany(body.missing_product_ids)
        }
      })
      .catch((caught: unknown) => {
        if (active) error = errorMessage(caught)
      })
    return () => {
      active = false
    }
  })
</script>

<Seo title="Your cart" description="The jars you have picked from Mama's Pantry." noindex />

<section class="page-stack">
  <h1 class="page-title">Your cart</h1>

  {#if removedNote}
    <p class="form-note" role="status">A jar that is no longer for sale was taken out of your cart.</p>
  {/if}

  {#if !cart.items.length}
    <p class="status">Your cart is empty for now.</p>
    <p><a class="button" href="/products">Browse all jars</a></p>
  {:else if error}
    <p class="status status-error" role="alert">{error}</p>
  {:else if summary}
    <div class="paper table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th scope="col">Jar</th>
            <th scope="col" class="number">Price</th>
            <th scope="col">Quantity</th>
            <th scope="col" class="number">Subtotal</th>
            <th scope="col"><span class="visually-hidden">Remove</span></th>
          </tr>
        </thead>
        <tbody>
          {#each summary.lines as line (line.product.id)}
            <tr>
              <td>
                <a href={`/products/${line.product.slug}`}>{line.product.name}</a>
                {#if !line.is_available}
                  <p class="form-error">
                    {line.product.stock ? `Only ${line.product.stock} left. Please lower the quantity.` : 'Sold out. Please remove this jar.'}
                  </p>
                {/if}
              </td>
              <td class="number">{formatPrice(line.product.price_cents)}</td>
              <td>
                {#if line.product.stock}
                  <QuantityPicker
                    label={`Jars of ${line.product.name}`}
                    value={line.quantity}
                    max={Math.min(line.product.stock, MAX_JARS_PER_LINE)}
                    onchange={(next) => cart.setQuantity(line.product.id, next)}
                  />
                {/if}
              </td>
              <td class="number">{line.is_available ? formatPrice(line.subtotal_cents) : '—'}</td>
              <td>
                <button class="button button-quiet" type="button" onclick={() => cart.remove(line.product.id)}>
                  Remove<span class="visually-hidden"> {line.product.name}</span>
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
        <tfoot>
          <tr>
            <th scope="row" colspan="3">Total</th>
            <td class="number">{formatPrice(summary.total_cents)}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <p class="cart-actions">
      <a href="/products">Keep browsing</a>
      {#if canCheckOut}
        <a class="button" href="/checkout">Go to checkout</a>
      {/if}
    </p>
  {:else}
    <p class="status" aria-live="polite">Counting the jars…</p>
  {/if}
</section>

<style>
  .cart-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-md);
  }
</style>
