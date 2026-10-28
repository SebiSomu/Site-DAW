<script lang="ts">
  import type { ProductSummary } from '../api/types'
  import { formatPrice } from '../format'
  import JarArt from './JarArt.svelte'

  let { product }: { product: ProductSummary } = $props()
</script>

<article class="paper index-card sway">
  <span class="tape" aria-hidden="true"></span>
  {#if product.image}
    <img src={product.image.url} alt={product.image.alt_text} width="200" height="200" loading="lazy" />
  {:else}
    <JarArt {product} />
  {/if}
  <h3><a href={`/products/${product.slug}`}>{product.name}</a></h3>
  <p class="meta">{product.category.name} · {product.weight_grams} g</p>
  <p class="price">{formatPrice(product.price_bani)}</p>
  {#if product.stock === 0}
    <p class="sold-out">Sold out</p>
  {/if}
</article>
