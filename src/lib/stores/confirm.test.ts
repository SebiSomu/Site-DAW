import { describe, expect, it } from 'vitest'
import { ConfirmStore } from './confirm.svelte'

describe('ConfirmStore', () => {
  it('resolves true when confirmed and closes', async () => {
    const store = new ConfirmStore()
    const answer = store.ask({ title: 'Cancel order 3?' })
    expect(store.current?.title).toBe('Cancel order 3?')
    store.answer(true)
    await expect(answer).resolves.toBe(true)
    expect(store.current).toBeNull()
  })

  it('resolves false when dismissed', async () => {
    const store = new ConfirmStore()
    const answer = store.ask({ title: 'Remove this photo?' })
    store.answer(false)
    await expect(answer).resolves.toBe(false)
  })

  it('fills in default labels', () => {
    const store = new ConfirmStore()
    void store.ask({ title: 'Delete?' })
    expect(store.current).toMatchObject({ message: '', confirmLabel: 'Yes', cancelLabel: 'Keep it' })
  })

  it('declines an older question when a new one opens', async () => {
    const store = new ConfirmStore()
    const first = store.ask({ title: 'First?' })
    const second = store.ask({ title: 'Second?' })
    await expect(first).resolves.toBe(false)
    expect(store.current?.title).toBe('Second?')
    store.answer(true)
    await expect(second).resolves.toBe(true)
  })
})
