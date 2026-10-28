<script lang="ts">
  import { ApiError, api, errorMessage } from '../lib/api/client'
  import type { ProductDetail } from '../lib/api/types'
  import Seo from '../lib/components/Seo.svelte'
  import { formatDate, formatPrice, formatStars } from '../lib/format'

  let { slug }: { slug: string } = $props()

  let product = $state<ProductDetail | null>(null)
  let error = $state('')
  let missing = $state(false)

  const images = $derived(
    product?.images.length ? product.images : [{ url: '/images/jar-placeholder.svg', alt_text: `Jar of ${product?.name}` }],
  )
  const pricePer100g = $derived(product ? formatPrice(Math.round((product.price_bani * 100) / product.weight_grams)) : '')

  $effect(() => {
    api
      .get<{ product: ProductDetail }>(`/products/${encodeURIComponent(slug)}`)
      .then((body) => (product = body.product))
      .catch((caught: unknown) => {
        missing = caught instanceof ApiError && caught.status === 404
        error = errorMessage(caught)
      })
  })
</script>

{#if product}
  <Seo
    title={product.name}
    description={`${product.name}, ${product.weight_grams} g, ${formatPrice(product.price_bani)}. ${product.description}`}
    image={product.image?.url}
  />

  <nav aria-label="Breadcrumb">
    <ol class="breadcrumb">
      <li><a href="/">Home</a></li>
      <li><a href="/products">All jars</a></li>
      <li><a href={`/products?category=${product.category.slug}`}>{product.category.name}</a></li>
      <li aria-current="page">{product.name}</li>
    </ol>
  </nav>

  <article class="product">
    <div class="gallery">
      {#each images as image, index (image.url)}
        <img src={image.url} alt={image.alt_text} width="480" height="480" loading={index === 0 ? 'eager' : 'lazy'} />
      {/each}
    </div>

    <div class="details">
      <h1>{product.name}</h1>
      <p class="price">{formatPrice(product.price_bani)}</p>
      {#if product.average_rating !== null}
        <p>
          <span aria-hidden="true">{formatStars(product.average_rating)}</span>
          {product.average_rating} out of 5 ({product.reviews.length}
          {product.reviews.length === 1 ? 'review' : 'reviews'})
        </p>
      {/if}
      <p>{product.description}</p>

      <table>
        <caption>About this jar</caption>
        <tbody>
          <tr><th scope="row">Category</th><td>{product.category.name}</td></tr>
          <tr><th scope="row">Net weight</th><td>{product.weight_grams} g</td></tr>
          <tr><th scope="row">Price per 100 g</th><td>{pricePer100g}</td></tr>
          <tr><th scope="row">Ingredients</th><td>{product.ingredients.join(', ')}</td></tr>
          <tr>
            <th scope="row">Availability</th>
            <td>{product.stock > 0 ? `In stock (${product.stock} jars)` : 'Sold out'}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </article>

  <section class="reviews" aria-labelledby="reviews-heading">
    <h2 id="reviews-heading">Reviews</h2>
    {#if product.reviews.length}
      <ul>
        {#each product.reviews as review (review.id)}
          <li>
            <p>
              <span aria-hidden="true">{formatStars(review.rating)}</span>
              <span class="visually-hidden">{review.rating} out of 5 stars</span>
              <strong>{review.author}</strong>,
              <time datetime={review.created_at}>{formatDate(review.created_at)}</time>
            </p>
            {#if review.comment}
              <p>{review.comment}</p>
            {/if}
          </li>
        {/each}
      </ul>
    {:else}
      <p>No reviews yet. Be the first to tell Mum what you think.</p>
    {/if}
  </section>
{:else if error}
  <Seo title={missing ? 'Jar not found' : 'Something went wrong'} description={error} noindex />
  <h1>{missing ? 'This jar is not on our shelves' : 'Something went wrong'}</h1>
  <p role="alert">{error}</p>
  <p><a href="/products">Browse all jars</a></p>
{:else}
  <p aria-live="polite">Opening the jar…</p>
{/if}

<style>
  .breadcrumb {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0 0 1rem;
    padding: 0;
    list-style: none;
    font-size: 0.9rem;
  }

  .breadcrumb li + li::before {
    content: '/';
    margin-right: 0.5rem;
    color: #6b4f53;
  }

  .breadcrumb a {
    color: #8b2d3a;
  }

  .product {
    display: grid;
    gap: 1.5rem;
  }

  @media (min-width: 768px) {
    .product {
      grid-template-columns: 1fr 1fr;
    }
  }

  .gallery {
    display: grid;
    gap: 0.75rem;
  }

  .gallery img {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 0.75rem;
  }

  h1 {
    margin: 0;
  }

  .price {
    font-size: 1.5rem;
    font-weight: 700;
    color: #8b2d3a;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  caption {
    text-align: left;
    font-weight: 700;
    padding-bottom: 0.5rem;
  }

  th,
  td {
    padding: 0.5rem;
    border-bottom: 1px solid #e6d5c8;
    text-align: left;
    vertical-align: top;
  }

  .reviews ul {
    display: grid;
    gap: 1rem;
    padding: 0;
    list-style: none;
  }

  .reviews p {
    margin: 0;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
</style>
