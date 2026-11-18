import type { NavLink } from './navigation'

export const MAX_PHOTO_BYTES = 12 * 1024 * 1024
export const PHOTO_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
export const PHOTO_ACCEPT = PHOTO_EXTENSIONS.join(',')
export const LOW_STOCK = 5
const MAX_SLUG_LENGTH = 140
const LEI_PATTERN = /^\d{1,5}(?:[.,]\d{1,2})?$/

export const ADMIN_LINKS: NavLink[] = [
  { href: '/admin', label: 'Dashboard' },
  { href: '/admin/products', label: 'Jars' },
  { href: '/admin/orders', label: 'Orders' },
  { href: '/admin/messages', label: 'Messages' },
  { href: '/admin/activity-log', label: 'Activity log' },
]

export const ORDER_STATUSES = [
  { code: 'pending_payment', name: 'Awaiting payment' },
  { code: 'paid', name: 'Paid' },
  { code: 'confirmed', name: 'Confirmed' },
  { code: 'shipped', name: 'Shipped' },
  { code: 'delivered', name: 'Delivered' },
  { code: 'cancelled', name: 'Cancelled' },
]

const STEP_LABELS: Record<string, string> = {
  confirmed: 'Mark as confirmed',
  shipped: 'Mark as shipped',
  delivered: 'Mark as delivered',
}

export function parseLei(text: string): number | null {
  const value = text.trim()
  if (!LEI_PATTERN.test(value)) return null
  const [lei, bani = ''] = value.replace(',', '.').split('.')
  const cents = Number(lei) * 100 + Number(bani.padEnd(2, '0'))
  return cents > 0 ? cents : null
}

export function toLeiInput(cents: number): string {
  return (cents / 100).toFixed(2)
}

export function ingredientsFrom(text: string): string[] {
  const names: string[] = []
  for (const part of text.split(/[,\n]/)) {
    const name = part.trim().toLowerCase()
    if (name && !names.includes(name)) names.push(name)
  }
  return names
}

export function slugify(text: string): string {
  const ascii = text.normalize('NFKD').replace(/[̀-ͯ]/g, '')
  const slug = ascii
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug.slice(0, MAX_SLUG_LENGTH).replace(/-+$/, '')
}

export function checkPhoto(file: Pick<File, 'name' | 'size'>): string | null {
  const dot = file.name.lastIndexOf('.')
  const extension = dot > 0 ? file.name.slice(dot).toLowerCase() : ''
  if (!PHOTO_EXTENSIONS.includes(extension)) return 'Only .jpg, .jpeg, .png and .webp photos can be uploaded.'
  if (file.size === 0) return 'This file is empty.'
  if (file.size > MAX_PHOTO_BYTES) return 'This file is larger than 12 MB. Please choose a smaller photo.'
  return null
}

export function stepLabel(code: string, wasPaid: boolean): string {
  if (code === 'cancelled') return wasPaid ? 'Cancel and refund' : 'Cancel order'
  return STEP_LABELS[code] ?? code
}

export function hrefWithQuery(path: string, params: Record<string, string | number | null | undefined>): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === '') continue
    if (key === 'page' && Number(value) === 1) continue
    query.set(key, String(value))
  }
  const search = query.toString()
  return search ? `${path}?${search}` : path
}

export function positiveInt(value: string | null): number | null {
  return value && /^[1-9][0-9]{0,5}$/.test(value) ? Number(value) : null
}
