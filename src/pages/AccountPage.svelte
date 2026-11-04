<script lang="ts">
  import { api, errorMessage } from '../lib/api/client'
  import type { Address } from '../lib/api/types'
  import AddressForm from '../lib/components/AddressForm.svelte'
  import AuthGate from '../lib/components/AuthGate.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { router } from '../lib/router/router.svelte'
  import { auth } from '../lib/stores/auth.svelte'

  let addresses = $state<Address[]>([])
  let error = $state('')

  const signedIn = $derived(!!auth.user)

  $effect(() => {
    if (!signedIn) return
    api
      .get<{ addresses: Address[] }>('/addresses')
      .then((body) => (addresses = body.addresses))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  async function removeAddress(id: number): Promise<void> {
    error = ''
    try {
      await api.delete(`/addresses/${id}`)
      addresses = addresses.filter((address) => address.id !== id)
    } catch (caught) {
      error = errorMessage(caught)
    }
  }

  async function logOut(): Promise<void> {
    error = ''
    try {
      await auth.logout()
      router.navigate('/')
    } catch (caught) {
      error = errorMessage(caught)
    }
  }
</script>

<Seo title="My account" description="Your details, delivery addresses and orders." noindex />

<AuthGate>
  <section class="page-stack">
    <h1 class="page-title">My account</h1>
    {#if error}
      <p class="form-error" role="alert">{error}</p>
    {/if}
    <div class="two-columns">
      <section class="paper sheet" aria-labelledby="my-addresses">
        <h2 id="my-addresses">My addresses</h2>
        {#if addresses.length}
          <ul class="address-list">
            {#each addresses as address (address.id)}
              <li>
                <span>{address.one_line}</span>
                <button class="button button-quiet" type="button" onclick={() => removeAddress(address.id)}>
                  Remove<span class="visually-hidden"> {address.one_line}</span>
                </button>
              </li>
            {/each}
          </ul>
        {:else}
          <p>You have not saved an address yet.</p>
        {/if}
        <h3>Add an address</h3>
        <AddressForm onsaved={(address) => (addresses = [address, ...addresses])} />
      </section>

      <section class="paper sheet" aria-labelledby="my-details">
        <h2 id="my-details">My details</h2>
        <p>{auth.user?.first_name} {auth.user?.last_name}</p>
        <p>{auth.user?.email}</p>
        {#if auth.user?.phone}
          <p>{auth.user.phone}</p>
        {/if}
        <p><a class="button" href="/account/orders">See my orders</a></p>
        <p><button class="button button-quiet" type="button" onclick={logOut}>Log out</button></p>
      </section>
    </div>
  </section>
</AuthGate>

<style>
  .address-list {
    display: grid;
    gap: var(--space-sm);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .address-list li {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-sm);
  }
</style>
