<script lang="ts">
  import { ApiError, api, errorMessage } from '../lib/api/client'
  import type { ProductDetail } from '../lib/api/types'
  import JarArt from '../lib/components/JarArt.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatDate, formatPrice, formatStars } from '../lib/format'

  let { slug }: { slug: string } = $props()

  let product = $state<ProductDetail | null>(null)
  let error = $state('')
  let missing = $state(false)

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
      {#each product.images as image, index (image.url)}
        <figure class="paper">
          <span class="tape" aria-hidden="true"></span>
          <img src={image.url} alt={image.alt_text} width="480" height="480" loading={index === 0 ? 'eager' : 'lazy'} />
        </figure>
      {:else}
        <figure class="paper">
          <span class="tape" aria-hidden="true"></span>
          <JarArt {product} />
        </figure>
      {/each}
    </div>

    <div class="details">
      <h1>{product.name}</h1>
      <p class="price product-price">{formatPrice(product.price_bani)}</p>
      {#if product.average_rating !== null}
        <p>
          <span aria-hidden="true">{formatStars(product.average_rating)}</span>
          {product.average_rating} out of 5 ({product.reviews.length}
          {product.reviews.length === 1 ? 'review' : 'reviews'})
        </p>
      {/if}
      <p class="description">{product.description}</p>

      <div class="paper pantry-label table-scroll">
      <table class="label-table">
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
    </div>
  </article>

  <section class="reviews" aria-labelledby="reviews-heading">
    <h2 id="reviews-heading">Reviews</h2>
    {#if product.reviews.length}
      <ul>
        {#each product.reviews as review (review.id)}
          <li class="paper review">
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
      <p class="status">No reviews yet. Be the first to tell Mum what you think.</p>
    {/if}
  </section>
{:else if error}
  <Seo title={missing ? 'Jar not found' : 'Something went wrong'} description={error} noindex />
  <h1>{missing ? 'This jar is not on our shelves' : 'Something went wrong'}</h1>
  <p class="status status-error" role="alert">{error}</p>
  <p><a href="/products">Browse all jars</a></p>
{:else}
  <p class="status" aria-live="polite">Opening the jar…</p>
{/if}


<style>
  .breadcrumb {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-xs);
    margin: 0 0 var(--space-xl);
    padding: 0;
    list-style: none;
    font-size: var(--text-sm);
  }

  .breadcrumb li + li::before {
    content: '/';
    margin-right: var(--space-xs);
    color: var(--color-ink-soft);
  }

  .product {
    display: grid;
    gap: var(--space-xl);
  }

  @media (min-width: 600px) {
    .product {
      grid-template-columns: 5fr 6fr;
      align-items: start;
    }
  }

  .gallery {
    display: grid;
    gap: var(--space-xl);
  }

  .gallery figure {
    margin: 0;
    padding: var(--space-md);
    rotate: -1deg;
  }

  .gallery img {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    background: var(--color-paper-shade);
  }

  .details {
    display: grid;
    gap: var(--space-md);
    align-content: start;
  }

  .details h1 {
    font-size: clamp(2.6rem, 2rem + 2.5vw, 4rem);
  }

  .product-price {
    font-size: 2rem;
  }

  .description {
    max-width: 38rem;
    font-size: var(--text-lg);
  }

  .pantry-label {
    margin-top: var(--space-md);
    padding: var(--space-lg);
    background: var(--color-kraft-light);
    border-radius: var(--radius-paper);
  }

  .reviews {
    display: grid;
    gap: var(--space-lg);
    margin-top: var(--space-2xl);
  }

  .reviews ul {
    display: grid;
    gap: var(--space-xl);
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr));
    margin: 0;
    padding: var(--space-md) 0 0;
    list-style: none;
  }

  .review {
    display: grid;
    gap: var(--space-xs);
    padding: var(--space-lg);
  }
</style>
