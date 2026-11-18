<script lang="ts">
  import type { ProductSummary } from '../api/types'
  import { formatPrice } from '../format'
  import { jarPhoto } from '../jars'
  import JarArt from './JarArt.svelte'

  let { product }: { product: ProductSummary } = $props()

  const photo = $derived(jarPhoto(product))
</script>

<article class="paper index-card sway">
  <span class="tape" aria-hidden="true"></span>
  {#if product.image}
    <img src={product.image.url} alt={product.image.alt_text} width="200" height="200" loading="lazy" />
  {:else if photo}
    <img
      src={photo.src}
      srcset={photo.srcset}
      sizes="(min-width: 1024px) 17rem, (min-width: 600px) 45vw, 90vw"
      alt={photo.alt}
      width="512"
      height="512"
      loading="lazy"
    />
  {:else}
    <JarArt {product} />
  {/if}
  <h3><a href={`/products/${product.slug}`}>{product.name}</a></h3>
  <p class="meta">{product.category.name} · {product.weight_grams} g</p>
  <p class="price">{formatPrice(product.price_cents)}</p>
  {#if product.stock === 0}
    <p class="sold-out">Sold out</p>
  {/if}
</article>
