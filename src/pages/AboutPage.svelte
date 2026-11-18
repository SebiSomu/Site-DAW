<script lang="ts">
  import HarvestCalendar from '../lib/components/HarvestCalendar.svelte'
  import Seo from '../lib/components/Seo.svelte'
  import { SEASONS, productHref } from '../lib/seasons'

  const RULES = [
    'If you would not eat the fruit fresh, it does not go in the pot.',
    'Never walk away from a pot on the fire.',
    'A clean spoon for every taste.',
    'Only what is on the label goes in the jar.',
    'Write the date on every lid.',
    'When in doubt, give it ten more minutes.',
  ]

  const PEOPLE = [
    {
      name: 'Mum',
      title: 'Head of the copper pot',
      duties:
        'Picks, pits, stirs and tastes. She has the final word on whether a batch is good enough to sell, and the answer is not always yes.',
    },
    {
      name: 'Her son',
      title: 'Head of anything with a screen',
      duties:
        "Built this shop, writes the labels when Mum's handwriting gets too enthusiastic, and carries the crates up from the cellar.",
    },
    {
      name: 'The neighbours',
      title: 'Official tasters',
      duties: 'Unpaid and never once late. They try every new batch and are, frankly, too polite to be much help.',
    },
  ]

  const QUESTIONS = [
    {
      question: 'Is it really all homemade?',
      answer:
        "Every jar is cooked in Mum's kitchen, in small batches, and filled by hand. That is also why some jars sell out and only come back when their fruit does.",
    },
    {
      question: 'What goes into the jars?',
      answer:
        'Fruit, usually some sugar and a little lemon. The fruit butters have no added sugar at all. Every jar lists its ingredients on its own page, and nothing else goes in.',
    },
    {
      question: 'Why is my favourite jar missing?',
      answer:
        'Because its fruit is out of season, or the batch is finished. The shop only sells jars that are really standing on the pantry shelf, so check back when the season comes round.',
    },
    {
      question: 'How should I keep an opened jar?',
      answer:
        'In the fridge with the lid on, and always with a clean spoon. Mum would also like you to know that it tastes best on warm bread.',
    },
  ]
</script>

<Seo
  title="About us"
  description="Meet the family behind Mum's Homemade Jams: a copper pot, a family orchard, an old recipe notebook and a year that follows the fruit."
  path="/about"
/>

<div class="stack">
  <section class="split about-hero" aria-labelledby="about-title">
    <div class="hero-text">
      <p class="eyebrow">Hello, and welcome to our kitchen</p>
      <h1 id="about-title">About us</h1>
      <p class="lede">
        We are a mother and her son. She makes the jam. He built this shop, mostly so the neighbours would stop knocking
        at seven in the morning to ask whether there was any plum butter left.
      </p>
      <p>
        Every jar on these shelves starts the same way: fruit picked when it is ready and not a day before, washed by
        hand, and one copper pot. Mum stirs, tastes, waits and tastes again, and nothing goes into a jar until she is
        happy with it. It is an afternoon nobody is allowed to rush.
      </p>
      <p>
        We are dedicated to this, and we put a great deal of love into it. Every batch gets our full attention, from
        sorting the fruit to writing the date on the lid. We cook in small batches, we take no shortcuts, and nothing
        leaves our kitchen that we would not happily put on our own breakfast table.
      </p>
      <p class="signoff">With love and a lot of patience, Mum and her son</p>
    </div>
    <HarvestCalendar />
  </section>

  <section class="split notebook" aria-labelledby="notebook-title">
    <div class="snapshot-holder reveal">
      <figure class="paper snapshot sway">
        <span class="tape" aria-hidden="true"></span>
        <img
          src="/images/plates/sour-cherry.jpg"
          alt="Watercolour of four Montmorency sour cherries beside pencil-drawn leaves, painted in 1915"
          width="960"
          height="1280"
          loading="lazy"
        />
        <figcaption>Sour cherries: the first jar she ever filled on her own.</figcaption>
      </figure>
    </div>
    <div class="notebook-text">
      <h2 id="notebook-title" class="reveal">The blue notebook</h2>
      <article class="paper recipe-card reveal reveal-late">
        <span class="tape" aria-hidden="true"></span>
        <p>
          Mum's recipes live in an old school notebook with a blue cover, soft at the corners and stained in places you
          can still smell. The first pages are in her mother's handwriting. The rest are hers.
        </p>
        <p>
          There are almost no measurements in it. Next to the quince preserve it simply says
          <q>cook until it turns the colour of honey</q>.
        </p>
        <p>
          We once tried to type the whole thing up properly. She read it, nodded, and went on cooking exactly the way she
          always had.
        </p>
      </article>
    </div>
  </section>

  <section class="year" aria-labelledby="year-title">
    <div class="section-head reveal">
      <h2 id="year-title">A year in the copper pot</h2>
      <p>Nothing here is made out of season, so the shop follows the calendar. This is roughly how Mum's year goes.</p>
    </div>
    <ol class="seasons">
      {#each SEASONS as season (season.id)}
        <li class="reveal">
          <article class="paper season" data-season={season.id} aria-labelledby={`season-${season.id}`}>
            <p class="season-months">{season.months}</p>
            <h3 id={`season-${season.id}`}>{season.title}</h3>
            <p>{season.story}</p>
            <ul class="tag-list" aria-label={`Jars made in ${season.months}`}>
              {#each season.jars as jar (jar.slug)}
                <li><a class="tag" href={productHref(jar.slug)}>{jar.name}</a></li>
              {/each}
            </ul>
          </article>
        </li>
      {/each}
    </ol>
  </section>

  <section class="split rules" aria-labelledby="rules-title">
    <div class="rules-text">
      <h2 id="rules-title" class="reveal">Mum's kitchen rules</h2>
      <p class="rules-quote reveal">Made with love, in a copper pot, the old-fashioned way.</p>
      <p class="reveal">
        They are pinned above the stove. Nobody remembers writing them down, and nobody has ever been allowed to break
        one.
      </p>
    </div>
    <div class="reveal reveal-late">
      <div class="paper recipe-card">
        <span class="tape" aria-hidden="true"></span>
        <ol class="hand-list" aria-label="The rules above the stove">
          {#each RULES as rule (rule)}
            <li>{rule}</li>
          {/each}
        </ol>
      </div>
    </div>
  </section>

  <section class="people" aria-labelledby="people-title">
    <h2 id="people-title" class="reveal">Who does what</h2>
    <ul class="people-grid">
      {#each PEOPLE as person (person.name)}
        <li class="reveal">
          <article class="paper note sway" aria-labelledby={`person-${person.name.replaceAll(' ', '-')}`}>
            <span class="tape" aria-hidden="true"></span>
            <h3 id={`person-${person.name.replaceAll(' ', '-')}`}>{person.name}</h3>
            <p class="note-title">{person.title}</p>
            <p>{person.duties}</p>
          </article>
        </li>
      {/each}
    </ul>
  </section>

  <section class="questions" aria-labelledby="questions-title">
    <h2 id="questions-title" class="reveal">Questions people ask at the gate</h2>
    <div class="question-list">
      {#each QUESTIONS as item (item.question)}
        <details class="paper question reveal">
          <summary>{item.question}</summary>
          <p>{item.answer}</p>
        </details>
      {/each}
    </div>
  </section>

  <section class="paper invite" aria-labelledby="invite-title">
    <div class="gingham invite-band" aria-hidden="true"></div>
    <div class="invite-body">
      <h2 id="invite-title">Come and see the shelf</h2>
      <p>Whatever is in season is on it. When a jar is gone, it is gone until next year.</p>
      <p><a class="button" href="/products">Browse all jars</a></p>
    </div>
  </section>
</div>

<style>
  .about-hero {
    align-items: start;
    margin-top: calc(var(--space-lg) * -1);
  }

  .hero-text,
  .notebook-text,
  .rules-text,
  .section-head {
    display: grid;
    gap: var(--space-lg);
    justify-items: start;
  }

  .eyebrow {
    font-family: var(--font-hand);
    font-size: 1.7rem;
    line-height: 1.1;
    color: var(--color-plum);
    rotate: -2deg;
  }

  .signoff {
    font-family: var(--font-hand);
    font-size: 1.7rem;
    line-height: 1.1;
    color: var(--color-plum);
    rotate: -1deg;
  }

  .lede {
    max-width: 34rem;
    font-size: var(--text-lg);
  }

  .hero-text p,
  .section-head p {
    max-width: 34rem;
  }

  .snapshot figcaption {
    padding-top: var(--space-sm);
    font-family: var(--font-hand);
    font-size: 1.45rem;
    line-height: 1.2;
    color: var(--color-ink-soft);
    text-align: center;
  }

  .notebook {
    align-items: start;
  }

  .snapshot-holder {
    justify-self: center;
    width: min(100%, 22rem);
  }

  .snapshot {
    --tilt: -2.5deg;
    --tape-tilt: 4deg;
    margin: 0;
    padding: var(--space-sm) var(--space-sm) var(--space-md);
  }

  .snapshot img {
    width: 100%;
    height: auto;
    aspect-ratio: 4 / 5;
    object-fit: cover;
  }

  .year {
    display: grid;
    gap: var(--space-xl);
  }

  .seasons {
    position: relative;
    display: grid;
    gap: var(--space-lg);
    margin: 0;
    padding: 0 0 0 var(--space-lg);
    list-style: none;
  }

  .seasons::before {
    content: '';
    position: absolute;
    inset: 0 auto 0 0.35rem;
    border-left: 2px dashed var(--color-kraft-deep);
  }

  .season {
    --season: var(--color-kraft);
    display: grid;
    gap: var(--space-sm);
    height: 100%;
    padding: var(--space-lg);
    border-top: 0.45rem solid var(--season);
  }

  .season::before {
    content: '';
    position: absolute;
    top: 1.4rem;
    left: calc(-1 * var(--space-lg) - 0.05rem);
    width: 0.9rem;
    height: 0.9rem;
    border: 2px solid var(--color-paper);
    border-radius: 50%;
    background: var(--season);
    box-shadow: 0 0 0 2px var(--season);
  }

  .season[data-season='late-spring'] {
    --season: #c8475a;
  }

  .season[data-season='high-summer'] {
    --season: var(--color-apricot);
  }

  .season[data-season='autumn'] {
    --season: var(--color-plum);
  }

  .season[data-season='first-frost'] {
    --season: var(--color-jam);
  }

  .season-months {
    font-size: var(--text-sm);
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--color-ink-soft);
  }

  .season .tag-list {
    margin-top: var(--space-xs);
  }

  .rules {
    align-items: start;
  }

  .rules-quote {
    max-width: 28rem;
    font-family: var(--font-label);
    font-size: clamp(1.5rem, 1.2rem + 1.2vw, 2.2rem);
    font-weight: 600;
    line-height: 1.2;
    color: var(--color-ink);
  }

  .hand-list {
    margin: 0;
    padding-left: calc(var(--space-lg) + 1.4rem);
    font-family: var(--font-hand);
    font-size: 1.55rem;
    line-height: 2rem;
    color: var(--color-plum);
  }

  .hand-list li::marker {
    font-weight: 700;
    color: var(--color-jam);
  }

  .people {
    display: grid;
    gap: var(--space-xl);
  }

  .people-grid {
    display: grid;
    gap: var(--space-xl) var(--space-lg);
    margin: 0;
    padding: var(--space-sm) 0 0;
    list-style: none;
  }

  .people-grid > li:nth-child(1) {
    --tilt: -1.2deg;
    --sway-delay: -1.4s;
    --tape-tilt: -4deg;
  }

  .people-grid > li:nth-child(2) {
    --tilt: 1deg;
    --sway-time: 6s;
    --sway-delay: -3s;
    --tape-tilt: 3deg;
  }

  .people-grid > li:nth-child(3) {
    --tilt: -0.5deg;
    --sway-time: 4.6s;
    --tape-tilt: -2deg;
  }

  .note {
    display: grid;
    gap: var(--space-xs);
    height: 100%;
    padding: var(--space-xl) var(--space-lg) var(--space-lg);
    background: #fff6d8;
  }

  .note-title {
    font-family: var(--font-label);
    font-weight: 600;
    color: var(--color-jam);
  }

  .questions {
    display: grid;
    gap: var(--space-xl);
  }

  .question-list {
    display: grid;
    gap: var(--space-md);
    max-width: 48rem;
  }

  .question summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-md);
    padding: var(--space-md) var(--space-lg);
    font-family: var(--font-label);
    font-size: var(--text-lg);
    font-weight: 600;
    cursor: pointer;
    list-style: none;
  }

  .question summary::-webkit-details-marker {
    display: none;
  }

  .question summary::after {
    content: '+';
    flex-shrink: 0;
    font-family: var(--font-hand);
    font-size: 2rem;
    line-height: 1;
    color: var(--color-jam);
    transition: rotate var(--t-ui) var(--ease-out);
  }

  .question[open] summary::after {
    rotate: 45deg;
  }

  .question p {
    padding: 0 var(--space-lg) var(--space-lg);
    max-width: 40rem;
  }

  .invite {
    overflow: hidden;
    text-align: center;
  }

  .invite-band {
    height: 0.9rem;
  }

  .invite-body {
    display: grid;
    justify-items: center;
    gap: var(--space-md);
    padding: var(--space-xl) var(--space-lg);
  }

  @media (min-width: 600px) {
    .seasons {
      grid-template-columns: repeat(2, 1fr);
      padding-left: 0;
    }

    .seasons::before,
    .season::before {
      display: none;
    }

    .people-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1024px) {
    .seasons {
      grid-template-columns: repeat(6, 1fr);
    }

    .seasons > li {
      grid-column: span 2;
    }

    .seasons > li:nth-last-child(-n + 2) {
      grid-column: span 3;
    }

    .people-grid {
      grid-template-columns: repeat(3, 1fr);
    }

    .rules-text {
      position: sticky;
      top: var(--space-xl);
    }
  }
</style>
