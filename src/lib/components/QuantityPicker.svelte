<script lang="ts">
  interface Props {
    label: string
    value: number
    max: number
    onchange: (value: number) => void
  }

  let { label, value, max, onchange }: Props = $props()

  function typed(event: Event & { currentTarget: HTMLInputElement }): void {
    const parsed = Number.parseInt(event.currentTarget.value, 10)
    const next = Math.min(Math.max(Number.isNaN(parsed) ? value : parsed, 1), max)
    event.currentTarget.value = String(next)
    onchange(next)
  }
</script>

<div class="quantity" role="group" aria-label={label}>
  <button class="icon-button" type="button" aria-label="One jar fewer" disabled={value <= 1} onclick={() => onchange(value - 1)}>
    <span aria-hidden="true">−</span>
  </button>
  <input type="number" inputmode="numeric" min="1" {max} {value} aria-label="Number of jars" onchange={typed} />
  <button class="icon-button" type="button" aria-label="One jar more" disabled={value >= max} onclick={() => onchange(value + 1)}>
    <span aria-hidden="true">+</span>
  </button>
</div>

<style>
  .quantity {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2xs);
  }

  input {
    width: 3.5rem;
    min-height: 2.75rem;
    padding: 0.3rem;
    border: 2px solid var(--color-kraft-deep);
    border-radius: var(--radius-paper);
    background: var(--color-paper);
    text-align: center;
    appearance: textfield;
  }

  input::-webkit-inner-spin-button,
  input::-webkit-outer-spin-button {
    appearance: none;
    margin: 0;
  }
</style>
