<script lang="ts">
  import { api, errorMessage } from '../api/client'

  interface Props {
    productId: number
    onposted: () => void
  }

  const STARS = [1, 2, 3, 4, 5]
  const VERDICTS = ['', 'Not for me', 'It was all right', 'Good', 'Very good', 'Loved it']

  let { productId, onposted }: Props = $props()

  let rating = $state(0)
  let comment = $state('')
  let busy = $state(false)
  let error = $state('')
  let hovered = $state(0)

  const shown = $derived(hovered || rating)

  async function post(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    if (rating < 1) {
      error = 'Please choose at least one star.'
      return
    }
    busy = true
    error = ''
    try {
      await api.post(`/products/${productId}/reviews`, { rating, comment })
      onposted()
    } catch (caught) {
      error = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<form class="paper review-form" onsubmit={post}>
  <h3>Tell Mama what you think</h3>
  <fieldset>
    <legend>Your rating</legend>
    <div class="rating">
      <div class="stars" role="presentation" onmouseleave={() => (hovered = 0)}>
        {#each STARS as star (star)}
          <label class="star" class:lit={star <= shown} onmouseenter={() => (hovered = star)}>
            <input class="visually-hidden" type="radio" name="rating" value={star} bind:group={rating} onchange={() => (error = '')} />
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path
                d="M12 2.8l2.75 5.6 6.15.9-4.45 4.33 1.05 6.12L12 16.86l-5.5 2.9 1.05-6.13L3.1 9.3l6.15-.9z"
              />
            </svg>
            <span class="visually-hidden">{star} {star === 1 ? 'star' : 'stars'}</span>
          </label>
        {/each}
      </div>
      <p class="verdict" aria-hidden="true">{VERDICTS[shown] || 'Tap a star'}</p>
    </div>
  </fieldset>
  <label class="field">
    Your comment (optional)
    <textarea rows="4" maxlength="2000" bind:value={comment}></textarea>
  </label>
  {#if error}
    <p class="form-error" role="alert">{error}</p>
  {/if}
  <p><button class="button" type="submit" disabled={busy}>Post my review</button></p>
</form>

<style>
  .review-form {
    display: grid;
    gap: var(--space-md);
    max-width: 40rem;
    padding: var(--space-lg);
  }

  fieldset {
    margin: 0;
    padding: 0;
    border: 0;
  }

  legend {
    padding: 0;
    font-size: var(--text-sm);
    font-weight: 700;
  }

  .rating {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-xs) var(--space-md);
    padding-top: var(--space-xs);
  }

  .stars {
    display: flex;
  }

  .star {
    display: grid;
    place-items: center;
    width: 2.75rem;
    height: 2.75rem;
    border-radius: 50%;
    cursor: pointer;
  }

  .star svg {
    width: 2rem;
    height: 2rem;
    fill: transparent;
    stroke: var(--color-kraft-deep);
    stroke-width: 1.4;
    stroke-linejoin: round;
    transition:
      fill 0.15s ease,
      stroke 0.15s ease,
      transform 0.15s ease;
  }

  .star.lit svg {
    fill: var(--color-apricot);
    stroke: var(--color-jam);
  }

  .star:hover svg {
    transform: scale(1.12);
  }

  .star:has(input:focus-visible) {
    outline: 3px solid var(--color-jam);
    outline-offset: 2px;
  }

  .verdict {
    margin: 0;
    min-width: 8rem;
    font-family: var(--font-hand);
    font-size: 1.6rem;
    color: var(--color-jam);
  }

  @media (prefers-reduced-motion: reduce) {
    .star svg {
      transition: none;
    }

    .star:hover svg {
      transform: none;
    }
  }
</style>
