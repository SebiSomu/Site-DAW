<script lang="ts">
  import { api, errorMessage } from '../api/client'

  interface Props {
    productId: number
    onposted: () => void
  }

  const STARS = [5, 4, 3, 2, 1]

  let { productId, onposted }: Props = $props()

  let rating = $state(5)
  let comment = $state('')
  let busy = $state(false)
  let error = $state('')

  async function post(event: SubmitEvent): Promise<void> {
    event.preventDefault()
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
  <h3>Tell Mum what you think</h3>
  <fieldset>
    <legend>Your rating</legend>
    <div class="stars">
      {#each STARS as star (star)}
        <label>
          <input type="radio" name="rating" value={star} bind:group={rating} />
          {star} {star === 1 ? 'star' : 'stars'}
        </label>
      {/each}
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

  .stars {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-xs) var(--space-md);
    padding-top: var(--space-xs);
  }

  .stars label {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2xs);
    min-height: 2.75rem;
  }
</style>
