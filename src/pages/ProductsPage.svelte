<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { Category, ProductPage, ProductSort } from '../lib/api/types'
  import ProductCard from '../lib/components/ProductCard.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { router } from '../lib/router/router.svelte'

  interface Filters {
    q?: string
    category?: string
    sort?: ProductSort
    page?: number
  }

  const DEFAULT_SORT: ProductSort = 'name'

  const SORT_OPTIONS: { value: ProductSort; label: string }[] = [
    { value: 'name', label: 'Name: A to Z' },
    { value: 'newest', label: 'Newest first' },
    { value: 'price-asc', label: 'Price: low to high' },
    { value: 'price-desc', label: 'Price: high to low' },
  ]

  let categories = $state<Category[]>([])
  let result = $state<ProductPage | null>(null)
  let error = $state('')

  const params = $derived(router.url.searchParams)
  const q = $derived(params.get('q') ?? '')
  const category = $derived(params.get('category') ?? '')
  const sort = $derived(SORT_OPTIONS.find((option) => option.value === params.get('sort'))?.value ?? DEFAULT_SORT)
  const page = $derived(Math.max(1, Number.parseInt(params.get('page') ?? '', 10) || 1))
  const activeCategory = $derived(categories.find((item) => item.slug === category))

  const heading = $derived(activeCategory?.name ?? 'All our jars')
  const description = $derived(
    activeCategory?.description ??
      'Browse every jam, preserve and fruit butter from Mum’s kitchen. Filter by category, search and sort by price.',
  )

  $effect(() => {
    api
      .get<{ categories: Category[] }>('/categories')
      .then((body) => (categories = body.categories))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  $effect(() => {
    const filters = { q, category, sort, page }
    let active = true
    error = ''
    api
      .get<ProductPage>('/products', filters)
      .then((body) => {
        if (active) result = body
      })
      .catch((caught: unknown) => {
        if (active) error = errorMessage(caught)
      })
    return () => {
      active = false
    }
  })

  function hrefFor(filters: Filters): string {
    const query = new URLSearchParams()
    if (filters.q) query.set('q', filters.q)
    if (filters.category) query.set('category', filters.category)
    if (filters.sort && filters.sort !== DEFAULT_SORT) query.set('sort', filters.sort)
    if (filters.page && filters.page > 1) query.set('page', String(filters.page))
    const search = query.toString()
    return search ? `/products?${search}` : '/products'
  }

  function applyFilters(event: SubmitEvent & { currentTarget: HTMLFormElement }): void {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const nextSort = SORT_OPTIONS.find((option) => option.value === data.get('sort'))?.value
    router.navigate(hrefFor({ q: String(data.get('q') ?? '').trim(), category, sort: nextSort }))
  }
</script>

<Seo title={heading} {description} path={hrefFor({ category })} />

<section class="catalogue">
  <h1>{heading}</h1>
  <p class="intro">{description}</p>

  <nav aria-label="Categories">
    <ul class="tag-list">
      <li><a class="tag" href={hrefFor({ q, sort })} aria-current={category ? undefined : 'page'}>All jars</a></li>
      {#each categories as item (item.slug)}
        <li>
          <a class="tag" href={hrefFor({ q, sort, category: item.slug })} aria-current={item.slug === category ? 'page' : undefined}>
            {item.name}
          </a>
        </li>
      {/each}
    </ul>
  </nav>

  <form class="filters" method="get" action="/products" role="search" onsubmit={applyFilters}>
    {#if category}
      <input type="hidden" name="category" value={category} />
    {/if}
    <label class="field">
      Search
      <input type="search" name="q" value={q} maxlength="100" placeholder="apricot, walnut…" />
    </label>
    <label class="field">
      Sort by
      <select name="sort" value={sort} onchange={(event) => event.currentTarget.form?.requestSubmit()}>
        {#each SORT_OPTIONS as option (option.value)}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </label>
    <button class="button" type="submit">Search</button>
  </form>

  {#if error}
    <p class="status status-error" role="alert">{error}</p>
  {:else if result}
    <p class="count" aria-live="polite">
      {result.total === 1 ? '1 jar' : `${result.total} jars`}{q ? ` matching “${q}”` : ''}
    </p>
    {#if result.items.length}
      <ul class="shelf">
        {#each result.items as product (product.id)}
          <li><ProductCard {product} /></li>
        {/each}
      </ul>
    {:else}
      <p class="status">No jars match your search. Try another word or <a href="/products">see all jars</a>.</p>
    {/if}
    {#if result.pages > 1}
      <nav class="pagination" aria-label="Pages">
        {#if page > 1}
          <a href={hrefFor({ q, category, sort, page: page - 1 })} rel="prev">Previous page</a>
        {/if}
        <span>Page {result.page} of {result.pages}</span>
        {#if page < result.pages}
          <a href={hrefFor({ q, category, sort, page: page + 1 })} rel="next">Next page</a>
        {/if}
      </nav>
    {/if}
  {:else}
    <p class="status" aria-live="polite">Fetching the jars from the pantry…</p>
  {/if}
</section>


<style>
  .catalogue {
    display: grid;
    gap: var(--space-lg);
  }

  .intro {
    max-width: 40rem;
    font-size: var(--text-lg);
  }

  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: end;
    gap: var(--space-sm) var(--space-md);
    padding: var(--space-md);
    background: var(--color-paper-shade);
  }

  .filters .field:first-of-type {
    flex: 1 1 14rem;
  }

  .count {
    font-family: var(--font-hand);
    font-size: 1.6rem;
    color: var(--color-ink-soft);
  }

  .pagination {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--space-md) var(--space-lg);
    padding-top: var(--space-lg);
    font-weight: 700;
  }
</style>
