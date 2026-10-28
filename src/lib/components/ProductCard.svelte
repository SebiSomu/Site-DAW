<script lang="ts">
  import type { ProductSummary } from '../api/types'
  import { formatPrice } from '../format'

  let { product }: { product: ProductSummary } = $props()
</script>

<article class="card">
  <a href={`/products/${product.slug}`}>
    <img
      src={product.image?.url ?? '/images/jar-placeholder.svg'}
      alt={product.image?.alt_text ?? `Jar of ${product.name}`}
      width="200"
      height="200"
      loading="lazy"
    />
    <h3>{product.name}</h3>
  </a>
  <p class="meta">{product.category.name} · {product.weight_grams} g</p>
  <p class="price">{formatPrice(product.price_bani)}</p>
  {#if product.stock === 0}
    <p class="sold-out">Sold out</p>
  {/if}
</article>

<style>
  .card {
    display: grid;
    gap: 0.25rem;
    padding: 0.75rem;
    border-radius: 0.75rem;
    background: #fff;
    box-shadow: 0 2px 8px rgb(59 31 36 / 0.08);
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  img {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 0.5rem;
  }

  h3 {
    margin: 0.5rem 0 0;
    font-size: 1.1rem;
  }

  p {
    margin: 0;
  }

  .meta {
    color: #6b4f53;
    font-size: 0.9rem;
  }

  .price {
    font-weight: 700;
    color: #8b2d3a;
  }

  .sold-out {
    font-size: 0.85rem;
    color: #7a5b00;
  }
</style>
