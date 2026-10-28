<script lang="ts">
  import Seo from '../lib/components/Seo.svelte'
</script>

<Seo
  title="Mum's Homemade Jams"
  description="Homemade jams, preserves and fruit butters made from Mum's recipes. Order jars with an old-fashioned taste online."
  path="/"
/>

<section class="hero">
  <h1>Mum's Homemade Jams</h1>
  <p>Made with love, in a copper pot, the old-fashioned way.</p>
  <p><a class="cta" href="/products">Browse all jars</a></p>
  <ul class="categories">
    <li><a href="/products?category=jams">Jams</a></li>
    <li><a href="/products?category=preserves">Preserves</a></li>
    <li><a href="/products?category=fruit-butters">Fruit butters</a></li>
    <li><a href="/products?category=seasonal-editions">Seasonal editions</a></li>
  </ul>
</section>

<style>
  .hero {
    display: grid;
    justify-items: center;
    gap: 0.75rem;
    padding: 3rem 0;
    text-align: center;
  }

  h1 {
    margin: 0;
    color: #8b2d3a;
    font-size: clamp(2rem, 6vw, 3.5rem);
  }

  p {
    margin: 0;
  }

  .cta {
    display: inline-block;
    padding: 0.6rem 1.4rem;
    border-radius: 999px;
    background: #8b2d3a;
    color: #fffaf3;
    text-decoration: none;
  }

  .categories {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
    padding: 0;
    list-style: none;
  }

  .categories a {
    color: #8b2d3a;
  }
</style>
