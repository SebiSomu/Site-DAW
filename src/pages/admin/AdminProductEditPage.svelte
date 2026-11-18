<script lang="ts">
  import { checkPhoto, ingredientsFrom, parseLei, PHOTO_ACCEPT, slugify, toLeiInput } from '../../lib/admin'
  import type { AdminProductDetail, AdminProductInput } from '../../lib/api/admin-types'
  import { ApiError, api, errorMessage } from '../../lib/api/client'
  import type { Category } from '../../lib/api/types'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { router } from '../../lib/router/router.svelte'
  import { auth } from '../../lib/stores/auth.svelte'

  let { id }: { id: string | null } = $props()

  let categories = $state<Category[]>([])
  let product = $state<AdminProductDetail | null>(null)
  let loadError = $state('')
  let missing = $state(false)

  let name = $state('')
  let slug = $state('')
  let categorySlug = $state('')
  let description = $state('')
  let price = $state('')
  let weight = $state('370')
  let stock = $state('0')
  let ingredients = $state('')
  let isActive = $state(true)

  let saving = $state(false)
  let saveError = $state('')
  let saved = $state(false)

  let photoInput = $state<HTMLInputElement | null>(null)
  let altText = $state('')
  let uploading = $state(false)
  let photoError = $state('')
  let photoBusy = $state(false)

  const isAdmin = $derived(auth.user?.role === 'admin')
  const isNew = $derived(id === null)
  const slugPreview = $derived(slug.trim() || slugify(name))
  const ready = $derived(isNew || product !== null)

  $effect(() => {
    if (!isAdmin) return
    api
      .get<{ categories: Category[] }>('/categories')
      .then((body) => {
        categories = body.categories
        categorySlug ||= body.categories[0]?.slug ?? ''
      })
      .catch((caught: unknown) => (loadError = errorMessage(caught)))
  })

  $effect(() => {
    if (!isAdmin || id === null) return
    api
      .get<{ product: AdminProductDetail }>(`/admin/products/${id}`)
      .then((body) => fill(body.product))
      .catch((caught: unknown) => {
        missing = caught instanceof ApiError && caught.status === 404
        loadError = errorMessage(caught)
      })
  })

  function fill(loaded: AdminProductDetail): void {
    product = loaded
    name = loaded.name
    slug = loaded.slug
    categorySlug = loaded.category.slug
    description = loaded.description
    price = toLeiInput(loaded.price_cents)
    weight = String(loaded.weight_grams)
    stock = String(loaded.stock)
    ingredients = loaded.ingredients.join(', ')
    isActive = loaded.is_active
  }

  function input(): AdminProductInput | null {
    const priceCents = parseLei(price)
    if (priceCents === null) {
      saveError = 'Write the price in lei, for example 24.50.'
      return null
    }
    return {
      name,
      slug: slug.trim() || undefined,
      category_slug: categorySlug,
      description,
      price_cents: priceCents,
      weight_grams: Number(weight),
      stock: Number(stock),
      ingredients: ingredientsFrom(ingredients),
      is_active: isActive,
    }
  }

  async function save(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    saveError = ''
    saved = false
    const body = input()
    if (!body) return
    saving = true
    try {
      if (isNew) {
        const created = (await api.post<{ product: AdminProductDetail }>('/admin/products', body)).product
        router.navigate(`/admin/products/${created.id}`)
        return
      }
      fill((await api.put<{ product: AdminProductDetail }>(`/admin/products/${id}`, body)).product)
      saved = true
    } catch (caught) {
      saveError = errorMessage(caught)
    } finally {
      saving = false
    }
  }

  async function remove(): Promise<void> {
    if (!product || !window.confirm(`Delete ${product.name} for good, with its photos?`)) return
    saving = true
    saveError = ''
    try {
      await api.delete(`/admin/products/${product.id}`)
      router.navigate('/admin/products')
    } catch (caught) {
      saveError = errorMessage(caught)
      saving = false
    }
  }

  async function upload(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    photoError = ''
    const file = photoInput?.files?.[0]
    if (!file) {
      photoError = 'Please choose a photo to upload.'
      return
    }
    const problem = checkPhoto(file)
    if (problem) {
      photoError = problem
      return
    }
    const form = new FormData()
    form.append('photo', file)
    form.append('alt_text', altText)
    uploading = true
    try {
      fill((await api.postForm<{ product: AdminProductDetail }>(`/admin/products/${id}/images`, form)).product)
      altText = ''
      if (photoInput) photoInput.value = ''
    } catch (caught) {
      photoError = errorMessage(caught)
    } finally {
      uploading = false
    }
  }

  async function photoAction(request: () => Promise<{ product: AdminProductDetail }>): Promise<void> {
    photoBusy = true
    photoError = ''
    try {
      fill((await request()).product)
    } catch (caught) {
      photoError = errorMessage(caught)
    } finally {
      photoBusy = false
    }
  }

  function makeMain(imageId: number): Promise<void> {
    return photoAction(() => api.post<{ product: AdminProductDetail }>(`/admin/images/${imageId}/main`))
  }

  function removePhoto(imageId: number): void {
    if (!window.confirm('Remove this photo?')) return
    void photoAction(() => api.delete<{ product: AdminProductDetail }>(`/admin/images/${imageId}`))
  }
</script>

<Seo title={isNew ? 'Add a jar' : `Edit ${product?.name ?? 'jar'}`} description="Change a jar's details and photos." noindex />

<AdminGate>
  <section class="page-stack">
    <p><a href="/admin/products">Back to all jars</a></p>
    {#if loadError}
      <h1 class="page-title">{missing ? 'We could not find this jar' : 'Something went wrong'}</h1>
      <p class="status status-error" role="alert">{loadError}</p>
    {:else if !ready}
      <p class="status" aria-live="polite">Taking the jar off the shelf…</p>
    {:else}
      <div class="edit-head">
        <h1 class="page-title">{isNew ? 'Add a jar' : product?.name}</h1>
        {#if product?.is_active}
          <a href={`/products/${product.slug}`}>See it in the shop</a>
        {/if}
      </div>

      <form class="paper sheet form-grid" onsubmit={save}>
        <label class="field">
          Name
          <input required maxlength="120" bind:value={name} />
        </label>
        <label class="field">
          Web address
          <input maxlength="140" pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder={slugify(name)} bind:value={slug} />
          <span class="field-hint">/products/{slugPreview || '…'}</span>
        </label>
        <label class="field">
          Shelf
          <select required bind:value={categorySlug}>
            {#each categories as category (category.slug)}
              <option value={category.slug}>{category.name}</option>
            {/each}
          </select>
        </label>
        <label class="field">
          Price in lei
          <input required inputmode="decimal" maxlength="9" placeholder="24.50" bind:value={price} />
        </label>
        <label class="field">
          Weight in grams
          <input type="number" required min="1" max="10000" bind:value={weight} />
        </label>
        <label class="field">
          Jars in stock
          <input type="number" required min="0" max="10000" bind:value={stock} />
        </label>
        <label class="field field-wide">
          Description
          <textarea required rows="4" maxlength="4000" bind:value={description}></textarea>
        </label>
        <label class="field field-wide">
          Ingredients
          <textarea rows="2" maxlength="1700" bind:value={ingredients}></textarea>
          <span class="field-hint">Separate them with commas, for example: apricots, sugar, lemon.</span>
        </label>
        <label class="check field-wide">
          <input type="checkbox" bind:checked={isActive} />
          Show this jar in the shop
        </label>
        {#if saveError}
          <p class="form-error field-wide" role="alert">{saveError}</p>
        {/if}
        {#if saved}
          <p class="form-note field-wide" role="status">Saved.</p>
        {/if}
        <p class="actions field-wide">
          <button class="button" type="submit" disabled={saving}>{isNew ? 'Add the jar' : 'Save changes'}</button>
          {#if product}
            {#if product.can_delete}
              <button class="button button-quiet" type="button" disabled={saving} onclick={remove}>Delete this jar</button>
            {:else}
              <span class="field-hint">This jar is in past orders, so it can be hidden but not deleted.</span>
            {/if}
          {/if}
        </p>
      </form>

      {#if product}
        <section class="paper sheet" aria-labelledby="photos-title">
          <h2 id="photos-title">Photos</h2>
          {#if product.images.length}
            <ul class="photos">
              {#each product.images as image (image.id)}
                <li class="photo">
                  <img src={image.url} alt={image.alt_text} width="320" height="320" loading="lazy" />
                  <p class="photo-alt">{image.alt_text}</p>
                  {#if image.position === 0}
                    <p class="tag">Main photo</p>
                  {:else}
                    <button class="button button-quiet" type="button" disabled={photoBusy} onclick={() => makeMain(image.id)}>
                      Make main photo
                    </button>
                  {/if}
                  <button class="button button-quiet" type="button" disabled={photoBusy} onclick={() => removePhoto(image.id)}>
                    Remove
                  </button>
                </li>
              {/each}
            </ul>
          {:else}
            <p>No photos yet, so the shop shows the illustrated jar instead.</p>
          {/if}

          <form class="form-grid upload" onsubmit={upload}>
            <label class="field">
              Photo
              <input type="file" required accept={PHOTO_ACCEPT} bind:this={photoInput} />
              <span class="field-hint">.jpg, .jpeg, .png or .webp, up to 12 MB. It is cleaned and saved as WebP.</span>
            </label>
            <label class="field">
              What the photo shows
              <input required maxlength="200" placeholder="A jar of apricot jam beside fresh apricots" bind:value={altText} />
              <span class="field-hint">Read aloud to people who cannot see the photo.</span>
            </label>
            {#if photoError}
              <p class="form-error field-wide" role="alert">{photoError}</p>
            {/if}
            <p class="field-wide">
              <button class="button" type="submit" disabled={uploading}>{uploading ? 'Uploading…' : 'Upload photo'}</button>
            </p>
          </form>
        </section>
      {/if}
    {/if}
  </section>
</AdminGate>

<style>
  .edit-head {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: var(--space-md);
  }

  .check {
    display: flex;
    align-items: center;
    gap: var(--space-xs);
    min-height: 2.75rem;
    font-weight: 700;
  }

  .check input {
    width: 1.25rem;
    height: 1.25rem;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-md);
  }

  .photos {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
    gap: var(--space-md);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .photo {
    display: grid;
    gap: var(--space-xs);
    align-content: start;
    justify-items: start;
  }

  .photo img {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: var(--radius-paper);
  }

  .photo-alt {
    font-size: var(--text-sm);
    color: var(--color-ink-soft);
  }

  .upload {
    padding-top: var(--space-md);
    border-top: 1px dashed var(--color-kraft-deep);
  }
</style>
