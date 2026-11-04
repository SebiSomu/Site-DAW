<script lang="ts">
  import { MediaQuery } from 'svelte/reactivity'
  import { cubicInOut } from 'svelte/easing'
  import { on } from 'svelte/events'
  import type { TransitionConfig } from 'svelte/transition'
  import { SHELVES, shelfHref } from '../shelves'

  type Direction = 'next' | 'prev'

  const AUTOPLAY_MS = 7000
  const SWIPE_PX = 50

  let current = $state(0)
  let direction = $state<Direction>('next')
  let stopped = $state(false)
  let hovered = $state(false)
  let focused = $state(false)
  let swipeStart: number | null = null

  const reducedMotion = new MediaQuery('prefers-reduced-motion: reduce')
  const playing = $derived(!stopped && !reducedMotion.current)

  $effect(() => {
    void current
    if (!playing || hovered || focused) return
    const timer = setTimeout(() => show(current + 1, 'next'), AUTOPLAY_MS)
    return () => clearTimeout(timer)
  })

  function show(index: number, towards: Direction): void {
    direction = towards
    current = (index + SHELVES.length) % SHELVES.length
  }

  function turn(_node: Element, { leaving }: { leaving: boolean }): TransitionConfig {
    const turning = leaving === (direction === 'next')
    return {
      duration: reducedMotion.current ? 0 : 750,
      easing: cubicInOut,
      css: (t) =>
        turning
          ? `z-index: 2; transform: rotateY(${(1 - t) * -100}deg); box-shadow: ${(1 - t) * 30}px 0 40px rgb(59 31 36 / ${(1 - t) * 0.35});`
          : 'z-index: 1;',
    }
  }

  function onKeydown(event: KeyboardEvent): void {
    if (event.key === 'ArrowRight') show(current + 1, 'next')
    else if (event.key === 'ArrowLeft') show(current - 1, 'prev')
    else return
    event.preventDefault()
  }

  function bookEvents(node: HTMLElement): () => void {
    const stops = [
      on(node, 'mouseenter', () => (hovered = true)),
      on(node, 'mouseleave', () => (hovered = false)),
      on(node, 'focusin', () => (focused = true)),
      on(node, 'focusout', () => (focused = false)),
      on(node, 'keydown', onKeydown),
    ]
    return () => stops.forEach((stop) => stop())
  }

  function swipeEvents(node: HTMLElement): () => void {
    const stops = [
      on(node, 'pointerdown', (event) => (swipeStart = event.clientX)),
      on(node, 'pointerup', onPointerUp),
      on(node, 'pointercancel', () => (swipeStart = null)),
    ]
    return () => stops.forEach((stop) => stop())
  }

  function onPointerUp(event: PointerEvent): void {
    if (swipeStart === null) return
    const distance = event.clientX - swipeStart
    swipeStart = null
    if (Math.abs(distance) < SWIPE_PX) return
    if (distance < 0) show(current + 1, 'next')
    else show(current - 1, 'prev')
  }
</script>

<section
  class="book"
  aria-roledescription="carousel"
  aria-label="Mum's recipe book"
  {@attach bookEvents}
>
  <div
    class="book-pages"
    aria-live={playing ? 'off' : 'polite'}
    {@attach swipeEvents}
  >
    {#each [current] as index (index)}
      {@const slide = SHELVES[index]}
      <div
        class="book-page"
        role="group"
        aria-roledescription="slide"
        aria-label={`${index + 1} of ${SHELVES.length}: ${slide.name}`}
        in:turn={{ leaving: false }}
        out:turn={{ leaving: true }}
      >
        <figure>
          <img src={slide.image} alt={slide.imageAlt} width="960" height="1280" draggable="false" />
        </figure>
        <div class="note">
          <h2>{slide.name}</h2>
          <p>{slide.note}</p>
          <p><a class="button" href={shelfHref(slide.slug)}>See the {slide.name.toLowerCase()}</a></p>
        </div>
      </div>
    {/each}
  </div>

  <div class="book-controls">
    <button class="icon-button" type="button" aria-label="Previous page" onclick={() => show(current - 1, 'prev')}>
      <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M12.5 4 6.5 10l6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
    </button>
    <div class="book-dots">
      {#each SHELVES as shelf, index (shelf.slug)}
        <button
          type="button"
          aria-label={`Show page ${index + 1}: ${shelf.name}`}
          aria-current={index === current}
          onclick={() => show(index, index < current ? 'prev' : 'next')}
        ></button>
      {/each}
    </div>
    {#if !reducedMotion.current}
      <button
        class="icon-button"
        type="button"
        aria-label={stopped ? 'Play slideshow' : 'Pause slideshow'}
        onclick={() => (stopped = !stopped)}
      >
        {#if stopped}
          <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M7 4.5v11l9-5.5z" fill="currentColor" /></svg>
        {:else}
          <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M6.5 4.5v11M13.5 4.5v11" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" /></svg>
        {/if}
      </button>
    {/if}
    <button class="icon-button" type="button" aria-label="Next page" onclick={() => show(current + 1, 'next')}>
      <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="m7.5 4 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
    </button>
  </div>
</section>
