<script lang="ts">
  import Seo from '../lib/components/Seo.svelte'
</script>

<Seo title="Page not found" description="This page does not exist. Head back to the shop to find your favourite jar." noindex />

<section class="empty">
  <img src="/images/jar-placeholder.svg" alt="" width="200" height="200" />
  <h1>This jar is empty</h1>
  <p>We could not find the page you were looking for.</p>
  <p><a class="button" href="/">Back to the shop</a></p>
</section>

<style>
  .empty {
    display: grid;
    justify-items: center;
    gap: var(--space-lg);
    padding-block: var(--space-xl);
    text-align: center;
  }

  img {
    width: 10rem;
    rotate: -6deg;
  }
</style>
