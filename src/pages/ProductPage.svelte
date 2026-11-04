<script lang="ts">
  import { ApiError, api, errorMessage } from '../lib/api/client'
  import type { ProductDetail } from '../lib/api/types'
  import JarArt from '../lib/components/JarArt.svelte'
  import QuantityPicker from '../lib/components/QuantityPicker.svelte'
  import ReviewForm from '../lib/components/ReviewForm.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { formatDate, formatPrice, formatStars } from '../lib/format'
  import { loginHref } from '../lib/redirects'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'
  import { MAX_JARS_PER_LINE, cart } from '../lib/stores/cart.svelte'

  let { slug }: { slug: string } = $props()

  let product = $state<ProductDetail | null>(null)
  let error = $state('')
  let missing = $state(false)

  let quantity = $state(1)
  let added = $state(false)
  let canReview = $state(false)

  const pricePer100g = $derived(product ? formatPrice(Math.round((product.price_cents * 100) / product.weight_grams)) : '')
  const productId = $derived(product?.id)
  const stock = $derived(product?.stock ?? 0)
  const inCart = $derived(productId ? cart.quantityOf(productId) : 0)
  const roomLeft = $derived(Math.min(stock, MAX_JARS_PER_LINE) - inCart)

  function load(): void {
    api
      .get<{ product: ProductDetail }>(`/products/${encodeURIComponent(slug)}`)
      .then((body) => (product = body.product))
      .catch((caught: unknown) => {
        missing = caught instanceof ApiError && caught.status === 404
        error = errorMessage(caught)
      })
  }

  $effect(load)

  $effect(() => {
    if (!auth.user || !productId) {
      canReview = false
      return
    }
    api
      .get<{ can_review: boolean }>(`/products/${productId}/reviews/eligibility`)
      .then((body) => (canReview = body.can_review))
      .catch(() => (canReview = false))
  })

  function addToCart(id: number): void {
    cart.add(id, Math.min(quantity, roomLeft), Math.min(stock, MAX_JARS_PER_LINE))
    quantity = 1
    added = true
  }

  function reviewPosted(): void {
    canReview = false
    load()
  }
</script>

{#if product}
  <Seo
    title={product.name}
    description={`${product.name}, ${product.weight_grams} g, ${formatPrice(product.price_cents)}. ${product.description}`}
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
      <p class="price product-price">{formatPrice(product.price_cents)}</p>
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

      <div class="buy">
        {#if roomLeft > 0}
          <QuantityPicker label="How many jars" value={Math.min(quantity, roomLeft)} max={roomLeft} onchange={(next) => (quantity = next)} />
          <button class="button" type="button" onclick={() => addToCart(product!.id)}>Add to cart</button>
        {:else if stock > 0}
          <p class="form-note">You have every jar we can offer in your cart.</p>
        {:else}
          <p class="sold-out">Sold out</p>
        {/if}
        <p class="buy-note" role="status">
          {#if added}
            {inCart === 1 ? '1 jar' : `${inCart} jars`} of this in your cart. <a href="/cart">View your cart</a>
          {/if}
        </p>
      </div>
    </div>
  </article>

  <section class="reviews" aria-labelledby="reviews-heading">
    <h2 id="reviews-heading">Reviews</h2>
    {#if canReview}
      <ReviewForm productId={product.id} onposted={reviewPosted} />
    {:else if auth.ready && !auth.user}
      <p>Bought this jar? <a href={loginHref(router.url.pathname)}>Log in to leave a review</a>.</p>
    {/if}
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

  .buy {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-md);
    margin-top: var(--space-md);
  }

  .buy-note {
    flex-basis: 100%;
    min-height: 1.6rem;
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
