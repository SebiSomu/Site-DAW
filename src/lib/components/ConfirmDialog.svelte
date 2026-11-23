<script lang="ts">
  import { confirmation } from '../stores/confirm.svelte'

  let dialog = $state<HTMLDialogElement>()
  let returnFocus: HTMLElement | null = null

  $effect(() => {
    if (!dialog) return
    if (confirmation.current && !dialog.open) {
      returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
      dialog.showModal()
    } else if (!confirmation.current && dialog.open) {
      dialog.close()
      returnFocus?.focus()
    }
  })

  function onBackdrop(event: MouseEvent): void {
    if (event.target === dialog) confirmation.answer(false)
  }

  function onCancel(event: Event): void {
    event.preventDefault()
    confirmation.answer(false)
  }
</script>

<dialog
  bind:this={dialog}
  class="confirm"
  aria-labelledby="confirm-title"
  aria-describedby="confirm-message"
  onclick={onBackdrop}
  oncancel={onCancel}
>
  {#if confirmation.current}
    <div class="paper confirm-card">
      <h2 id="confirm-title">{confirmation.current.title}</h2>
      {#if confirmation.current.message}
        <p id="confirm-message">{confirmation.current.message}</p>
      {/if}
      <div class="confirm-actions">
        <button class="button button-quiet" type="button" onclick={() => confirmation.answer(false)}>
          {confirmation.current.cancelLabel}
        </button>
        <button class="button" type="button" onclick={() => confirmation.answer(true)}>
          {confirmation.current.confirmLabel}
        </button>
      </div>
    </div>
  {/if}
</dialog>

<style>
  .confirm {
    width: min(28rem, calc(100vw - 2rem));
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--color-ink);
  }

  .confirm::backdrop {
    background: rgb(59 31 36 / 0.45);
    backdrop-filter: blur(2px);
  }

  .confirm[open] {
    animation: confirm-in 0.18s ease-out;
  }

  .confirm-card {
    display: grid;
    gap: var(--space-md);
    padding: var(--space-lg);
    border-top: 6px solid var(--color-jam);
  }

  h2 {
    margin: 0;
    font-family: var(--font-hand);
    font-size: 2rem;
    line-height: 1.1;
    color: var(--color-jam);
  }

  p {
    margin: 0;
  }

  .confirm-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: var(--space-sm);
  }

  @keyframes confirm-in {
    from {
      opacity: 0;
      transform: translateY(0.75rem) scale(0.98);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .confirm[open] {
      animation: none;
    }
  }
</style>
