<script lang="ts">
  import { LOW_STOCK } from '../../lib/admin'
  import type { AdminProductSummary } from '../../lib/api/admin-types'
  import { api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatPrice } from '../../lib/format'
  import { auth } from '../../lib/stores/auth.svelte'

  let products = $state<AdminProductSummary[] | null>(null)
  let error = $state('')
  let search = $state('')

  const isAdmin = $derived(auth.user?.role === 'admin')
  const shown = $derived(
    (products ?? []).filter((product) => product.name.toLowerCase().includes(search.trim().toLowerCase())),
  )

  $effect(() => {
    if (!isAdmin) return
    api
      .get<{ products: AdminProductSummary[] }>('/admin/products')
      .then((body) => (products = body.products))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })
</script>

<Seo title="Jars" description="Every jar in the shop, hidden ones included." noindex />

<AdminGate>
  <section class="page-stack">
    <div class="admin-head">
      <h1 class="page-title">Jars</h1>
      <a class="button" href="/admin/products/new">Add a jar</a>
    </div>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if !products}
      <p class="status" aria-live="polite">Counting the shelves…</p>
    {:else}
      <label class="field search">
        Find a jar
        <input type="search" maxlength="100" bind:value={search} />
      </label>
      <div class="paper table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Photo</th>
              <th scope="col">Jar</th>
              <th scope="col">Shelf</th>
              <th scope="col" class="number">Price</th>
              <th scope="col" class="number">Stock</th>
              <th scope="col">In the shop</th>
            </tr>
          </thead>
          <tbody>
            {#each shown as product (product.id)}
              <tr>
                <td>
                  {#if product.image}
                    <img class="thumb" src={product.image.url} alt="" width="48" height="48" loading="lazy" />
                  {:else}
                    <span class="field-hint">None</span>
                  {/if}
                </td>
                <th scope="row"><a href={`/admin/products/${product.id}`}>{product.name}</a></th>
                <td>{product.category.name}</td>
                <td class="number">{formatPrice(product.price_cents)}</td>
                <td class="number" class:low={product.stock <= LOW_STOCK}>
                  {product.stock === 0 ? 'Sold out' : product.stock}
                </td>
                <td>{product.is_active ? 'Shown' : 'Hidden'}</td>
              </tr>
            {:else}
              <tr><td colspan="6">No jar has that name.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
      <p class="field-hint">{products.length} jars in total.</p>
    {/if}
  </section>
</AdminGate>

<style>
  .admin-head {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-md);
  }

  .search {
    max-width: 22rem;
  }

  .thumb {
    display: block;
    width: 3rem;
    height: 3rem;
    object-fit: cover;
    border-radius: var(--radius-paper);
  }

  .low {
    font-weight: 700;
    color: var(--color-error);
  }
</style>
