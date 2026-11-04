<script lang="ts">
  import { api, errorMessage } from '../api/client'
  import type { Address } from '../api/types'

  const POSTAL_CODE_PATTERN = '[0-9]{6}'

  let { onsaved }: { onsaved: (address: Address) => void } = $props()

  let street = $state('')
  let city = $state('')
  let county = $state('')
  let postal_code = $state('')
  let busy = $state(false)
  let error = $state('')

  async function save(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    busy = true
    error = ''
    try {
      const body = await api.post<{ address: Address }>('/addresses', { street, city, county, postal_code })
      street = city = county = postal_code = ''
      onsaved(body.address)
    } catch (caught) {
      error = errorMessage(caught)
    } finally {
      busy = false
    }
  }
</script>

<form class="form-grid" onsubmit={save}>
  <label class="field field-wide">
    Street and number
    <input required maxlength="200" autocomplete="street-address" bind:value={street} />
  </label>
  <label class="field">
    City
    <input required maxlength="100" autocomplete="address-level2" bind:value={city} />
  </label>
  <label class="field">
    County
    <input required maxlength="50" autocomplete="address-level1" bind:value={county} />
  </label>
  <label class="field">
    Postal code (6 digits)
    <input required inputmode="numeric" pattern={POSTAL_CODE_PATTERN} maxlength="6" autocomplete="postal-code" bind:value={postal_code} />
  </label>
  {#if error}
    <p class="form-error field-wide" role="alert">{error}</p>
  {/if}
  <p class="field-wide"><button class="button button-quiet" type="submit" disabled={busy}>Save this address</button></p>
</form>
