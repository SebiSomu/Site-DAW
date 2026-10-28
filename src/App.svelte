<script lang="ts">
  type ApiStatus = 'se verifică' | 'conectat' | 'indisponibil'

  let apiStatus = $state<ApiStatus>('se verifică')

  $effect(() => {
    fetch('/api/health')
      .then((response) => {
        apiStatus = response.ok ? 'conectat' : 'indisponibil'
      })
      .catch(() => {
        apiStatus = 'indisponibil'
      })
  })
</script>

<main>
  <h1>Gemuri ca la mama acasă</h1>
  <p>Magazinul se pregătește. Borcanele sunt pe drum.</p>
  <p class="status">Server: <strong>{apiStatus}</strong></p>
</main>

<style>
  main {
    min-height: 100vh;
    display: grid;
    place-content: center;
    gap: 0.75rem;
    padding: 1rem;
    text-align: center;
    background: #fffaf3;
    color: #3b1f24;
    font-family: Georgia, serif;
  }

  h1 {
    margin: 0;
    color: #8b2d3a;
    font-size: clamp(2rem, 6vw, 3.5rem);
  }

  p {
    margin: 0;
  }

  .status {
    font-family: system-ui, sans-serif;
    font-size: 0.9rem;
  }
</style>
