import type { CartEntry } from '../api/types'

export const MAX_JARS_PER_LINE = 99

const STORAGE_KEY = 'mums-jams-cart'

type CartStorage = Pick<Storage, 'getItem' | 'setItem'>

function isCartEntry(value: unknown): value is CartEntry {
  const entry = value as CartEntry
  return Number.isInteger(entry?.product_id) && entry.product_id > 0 && Number.isInteger(entry.quantity) && entry.quantity > 0
}

function browserStorage(): CartStorage | null {
  try {
    return globalThis.localStorage ?? null
  } catch {
    return null
  }
}

export class CartStore {
  items = $state<CartEntry[]>([])
  private readonly storage: CartStorage | null

  constructor(storage: CartStorage | null = browserStorage()) {
    this.storage = storage
    this.items = this.read()
  }

  get count(): number {
    return this.items.reduce((sum, item) => sum + item.quantity, 0)
  }

  quantityOf(productId: number): number {
    return this.items.find((item) => item.product_id === productId)?.quantity ?? 0
  }

  add(productId: number, quantity: number, stock: number): void {
    this.setQuantity(productId, Math.min(this.quantityOf(productId) + quantity, stock))
  }

  setQuantity(productId: number, quantity: number): void {
    const clamped = Math.min(Math.floor(quantity), MAX_JARS_PER_LINE)
    if (!(clamped > 0)) {
      this.remove(productId)
    } else if (this.quantityOf(productId)) {
      this.save(this.items.map((item) => (item.product_id === productId ? { ...item, quantity: clamped } : item)))
    } else {
      this.save([...this.items, { product_id: productId, quantity: clamped }])
    }
  }

  remove(productId: number): void {
    this.save(this.items.filter((item) => item.product_id !== productId))
  }

  removeMany(productIds: number[]): void {
    this.save(this.items.filter((item) => !productIds.includes(item.product_id)))
  }

  clear(): void {
    this.save([])
  }

  private read(): CartEntry[] {
    try {
      const stored: unknown = JSON.parse(this.storage?.getItem(STORAGE_KEY) ?? '[]')
      return Array.isArray(stored) ? stored.filter(isCartEntry) : []
    } catch {
      return []
    }
  }

  private save(items: CartEntry[]): void {
    this.items = items
    try {
      this.storage?.setItem(STORAGE_KEY, JSON.stringify(items))
    } catch {
      return
    }
  }
}

export const cart = new CartStore()
