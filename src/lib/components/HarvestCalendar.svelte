<script lang="ts">
  import { harvestLabel, harvestRows, MONTH_NAMES } from '../harvest'
  import { productHref } from '../seasons'
  import FruitArt from './FruitArt.svelte'

  const MONTH_ABBREVIATIONS = MONTH_NAMES.map((name) => name.slice(0, 3))

  const rows = harvestRows()
  const currentMonth = new Date().getMonth()
</script>

<figure class="paper harvest">
  <span class="tape" aria-hidden="true"></span>
  <div class="plot" style={`--month: ${currentMonth}`}>
    <div class="now" aria-hidden="true"></div>
    <div class="head" aria-hidden="true">
      <span></span>
      <span class="months">
        {#each MONTH_ABBREVIATIONS as abbreviation (abbreviation)}
          <span>{abbreviation}</span>
        {/each}
      </span>
    </div>
    <ol class="rows">
      {#each rows as row (row.slug)}
        <li>
          <a href={productHref(row.slug)}>
            <span class="label">
              <svg class="fruit" viewBox="-28 -28 56 56" aria-hidden="true"><FruitArt fruit={row.fruit} /></svg>
              <span class="name">{row.name}</span>
              <span class="visually-hidden">, {harvestLabel(row)}</span>
            </span>
            <span class="track" aria-hidden="true">
              {#each row.spans as [first, last] (first)}
                <span class="bar" style={`grid-column: ${first} / ${last + 1}; background: ${row.colour}`}></span>
              {/each}
            </span>
          </a>
        </li>
      {/each}
    </ol>
  </div>
  <figcaption>What is on the fire, month by month. The shaded column is this month.</figcaption>
</figure>

<style>
  .harvest {
    margin: 0;
    padding: var(--space-xl) var(--space-md) var(--space-md);
  }

  .plot {
    --label: 8.6rem;
    position: relative;
    width: min(100%, 40rem);
    margin-inline: auto;
  }

  .now {
    position: absolute;
    top: 0;
    bottom: 0;
    left: calc(var(--label) + (100% - var(--label)) * var(--month) / 12);
    width: calc((100% - var(--label)) / 12);
    border-radius: 0.4rem;
    background: var(--color-tape);
    opacity: 0.55;
  }

  .head,
  a {
    position: relative;
    display: grid;
    grid-template-columns: var(--label) 1fr;
    align-items: center;
  }

  .months,
  .track {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
  }

  .months {
    padding-bottom: 0.3rem;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--color-ink-soft);
    text-align: center;
  }

  .rows {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  li + li {
    border-top: 1px dashed rgb(59 31 36 / 0.12);
  }

  a {
    min-height: 2.1rem;
    color: var(--color-ink);
    text-decoration: none;
  }

  .label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-width: 0;
  }

  .fruit {
    flex: none;
    width: 1.6rem;
    height: 1.6rem;
    overflow: visible;
  }

  .name {
    overflow: hidden;
    padding-right: 0.2em;
    font-family: var(--font-hand);
    font-size: 1.2rem;
    line-height: 1;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .track {
    align-items: center;
    height: 100%;
    background: repeating-linear-gradient(90deg, transparent 0 calc(100% / 12 - 1px), rgb(59 31 36 / 0.08) 0 calc(100% / 12));
  }

  .bar {
    height: 0.8rem;
    border-radius: 0.4rem;
    box-shadow: inset 0 -2px 0 rgb(0 0 0 / 0.14);
  }

  a:hover .name,
  a:focus-visible .name {
    text-decoration: underline;
    text-underline-offset: 0.2em;
  }

  figcaption {
    padding-top: var(--space-sm);
    font-family: var(--font-hand);
    font-size: 1.45rem;
    line-height: 1.2;
    color: var(--color-ink-soft);
    text-align: center;
  }

  @media (max-width: 599px) {
    .plot {
      --label: 7.4rem;
    }

    .name {
      font-size: 1rem;
    }

    .months span {
      justify-self: center;
      writing-mode: vertical-rl;
      rotate: 180deg;
    }
  }
</style>
