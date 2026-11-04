import { beforeEach, describe, expect, it } from 'vitest'
import { CartStore, MAX_JARS_PER_LINE } from './cart.svelte'

function fakeStorage(initial: string | null = null) {
  let stored = initial
  return {
    getItem: () => stored,
    setItem: (_key: string, value: string) => {
      stored = value
    },
    contents: () => stored,
  }
}

describe('CartStore', () => {
  let storage: ReturnType<typeof fakeStorage>
  let cart: CartStore

  beforeEach(() => {
    storage = fakeStorage()
    cart = new CartStore(storage)
  })

  it('adds jars and merges repeated products', () => {
    cart.add(1, 2, 10)
    cart.add(1, 1, 10)
    cart.add(2, 1, 10)
    expect(cart.items).toEqual([
      { product_id: 1, quantity: 3 },
      { product_id: 2, quantity: 1 },
    ])
    expect(cart.count).toBe(4)
  })

  it('never adds more jars than are in stock', () => {
    cart.add(1, 5, 3)
    cart.add(1, 5, 3)
    expect(cart.quantityOf(1)).toBe(3)
  })

  it('caps a line at the maximum the server accepts', () => {
    cart.setQuantity(1, 500)
    expect(cart.quantityOf(1)).toBe(MAX_JARS_PER_LINE)
  })

  it.each([0, -3, Number.NaN])('removes a line when its quantity becomes %s', (quantity) => {
    cart.add(1, 2, 10)
    cart.setQuantity(1, quantity)
    expect(cart.items).toEqual([])
  })

  it('removes several lines and clears', () => {
    cart.add(1, 1, 10)
    cart.add(2, 1, 10)
    cart.add(3, 1, 10)
    cart.removeMany([1, 3])
    expect(cart.items).toEqual([{ product_id: 2, quantity: 1 }])
    cart.clear()
    expect(cart.count).toBe(0)
  })

  it('survives a reload through storage', () => {
    cart.add(7, 2, 10)
    const reloaded = new CartStore(fakeStorage(storage.contents()))
    expect(reloaded.items).toEqual([{ product_id: 7, quantity: 2 }])
  })

  it.each(['not json', '{"a":1}', '[{"product_id":"1","quantity":2},{"product_id":1,"quantity":-2},null]'])(
    'ignores damaged storage: %s',
    (stored) => {
      expect(new CartStore(fakeStorage(stored)).items).toEqual([])
    },
  )

  it('works when storage is unavailable', () => {
    const noStorage = new CartStore(null)
    noStorage.add(1, 1, 10)
    expect(noStorage.count).toBe(1)
  })
})
