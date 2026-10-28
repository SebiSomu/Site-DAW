<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { ProductPage, ProductSummary } from '../lib/api/types'
  import Carousel from '../lib/components/Carousel.svelte'
  import ProductCard from '../lib/components/ProductCard.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { SHELVES, shelfHref } from '../lib/shelves'

  const FEATURED_COUNT = 4

  let featured = $state<ProductSummary[]>([])
  let error = $state('')

  $effect(() => {
    api
      .get<ProductPage>('/products', { sort: 'newest' })
      .then((body) => (featured = body.items.slice(0, FEATURED_COUNT)))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })
</script>

<Seo
  title="Mum's Homemade Jams"
  description="Homemade jams, preserves and fruit butters made from Mum's recipes. Order jars with an old-fashioned taste online."
  path="/"
/>

<div class="stack">
  <section class="split hero" aria-labelledby="hero-title">
    <div class="hero-text">
      <h1 id="hero-title">Mum's Homemade Jams</h1>
      <p class="hero-line">
        Jams, preserves and fruit butters from Mum's own recipes, cooked slowly in small batches and sold by the jar.
      </p>
      <p><a class="button" href="/products">Browse all jars</a></p>
    </div>
    <Carousel />
  </section>

  <section class="featured" aria-labelledby="featured-title">
    <div class="featured-head reveal">
      <h2 id="featured-title">Fresh on the shelf</h2>
      <a href="/products">See every jar</a>
    </div>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if featured.length}
      <ul class="shelf">
        {#each featured as product (product.id)}
          <li class="reveal"><ProductCard {product} /></li>
        {/each}
      </ul>
    {:else}
      <p class="status" aria-live="polite">Fetching the jars from the pantry…</p>
    {/if}
  </section>

  <section class="kitchen split" aria-labelledby="kitchen-title">
    <div class="kitchen-text">
      <h2 id="kitchen-title" class="reveal">How Mum fills a jar</h2>
      <p class="kitchen-quote reveal">Made with love, in a copper pot, the old-fashioned way.</p>
      <article class="paper recipe-card reveal reveal-late" aria-label="Mum's method">
        <span class="tape" aria-hidden="true"></span>
        <ul class="hand-list">
          <li>Fruit only while it is in season, picked ripe.</li>
          <li>One copper pot, a low fire and a long afternoon.</li>
          <li>Fruit butters simmered for hours, with no added sugar.</li>
          <li>Small batches, so every jar is filled by hand.</li>
        </ul>
      </article>
    </div>
    <div class="pinboard">
      <h3 class="visually-hidden">Pick a shelf</h3>
      <ul class="shelf pinboard-grid">
        {#each SHELVES as shelf (shelf.slug)}
          <li class="reveal">
            <figure class="paper plate sway">
              <span class="tape" aria-hidden="true"></span>
              <span class="plate-frame"><img src={shelf.image} alt={shelf.imageAlt} width="960" height="1280" loading="lazy" /></span>
              <figcaption><a href={shelfHref(shelf.slug)}>{shelf.name}</a></figcaption>
            </figure>
          </li>
        {/each}
      </ul>
    </div>
  </section>
</div>

<style>
  .hero-text {
    display: grid;
    gap: var(--space-lg);
    justify-items: start;
  }

  .hero-line {
    max-width: 30rem;
    font-size: var(--text-lg);
  }

  .featured {
    display: grid;
    gap: var(--space-lg);
  }

  .featured-head {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-sm);
  }

  .featured-head a {
    font-weight: 700;
  }

  .kitchen {
    align-items: start;
  }

  .kitchen-text {
    display: grid;
    gap: var(--space-lg);
  }

  @media (min-width: 1024px) {
    .kitchen-text {
      position: sticky;
      top: var(--space-xl);
    }
  }

  .kitchen-quote {
    max-width: 30rem;
    font-family: var(--font-label);
    font-size: clamp(1.5rem, 1.2rem + 1.2vw, 2.2rem);
    font-weight: 600;
    line-height: 1.2;
    color: var(--color-ink);
  }

  .hand-list {
    display: grid;
    margin: 0;
    padding-left: 1.2rem;
    font-family: var(--font-hand);
    font-size: 1.55rem;
    line-height: 2rem;
    color: var(--color-plum);
  }

  .pinboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .plate {
    margin: 0;
    padding: var(--space-sm) var(--space-sm) var(--space-xs);
  }

  .plate-frame {
    display: block;
    overflow: hidden;
  }

  .plate img {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    scale: 1.08;
  }

  .plate figcaption {
    padding-top: var(--space-xs);
    font-family: var(--font-hand);
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.2;
  }

  .plate a {
    color: var(--color-jam);
    text-decoration: none;
  }

  .plate a::after {
    content: '';
    position: absolute;
    inset: 0;
  }
</style>
