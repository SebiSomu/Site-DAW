<script lang="ts">
  import { SHELVES, shelfHref } from '../shelves'

  const year = new Date().getFullYear()
</script>

<footer class="site-footer">
  <div class="gingham" aria-hidden="true"></div>
  <div class="footer-inner page-width">
    <p class="footer-name">Mama's Pantry</p>
    <div class="footer-columns">
      <section aria-labelledby="footer-shop">
        <h2 id="footer-shop">The pantry</h2>
        <ul>
          <li><a href="/products">All jars</a></li>
          {#each SHELVES as shelf (shelf.slug)}
            <li><a href={shelfHref(shelf.slug)}>{shelf.name}</a></li>
          {/each}
        </ul>
      </section>
      <section aria-labelledby="footer-kitchen">
        <h2 id="footer-kitchen">From the kitchen</h2>
        <p>Made with love, in a copper pot, the old-fashioned way. All prices are in lei.</p>
        <p><a href="/about">Read our story</a></p>
        <p><a href="/contact">Write to us</a></p>
      </section>
      <section aria-labelledby="footer-credits">
        <h2 id="footer-credits">Picture credits</h2>
        <p class="footer-small">
          Fruit watercolours by Frank Muller (1889), Harriet L. Thompson (1915), L.C.C. Krieger (1935) and Elsie Lower
          Pomeroy (1912), from the
          <a href="https://commons.wikimedia.org/wiki/Category:USDA_Pomological_Watercolor_Collection" rel="noopener"
            >USDA Pomological Watercolor Collection</a
          >, public domain, via Wikimedia Commons.
        </p>
      </section>
    </div>
    <p class="footer-small">© {year} Mama's Pantry</p>
  </div>
</footer>
