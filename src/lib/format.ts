export function formatPrice(cents: number): string {
  return `${(cents / 100).toFixed(2)} lei`
}

const HAS_OFFSET = /(?:Z|[+-]\d{2}:?\d{2})$/

export function serverTime(iso: string): Date {
  return new Date(HAS_OFFSET.test(iso) ? iso : `${iso}Z`)
}

export function formatDate(iso: string): string {
  return serverTime(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

export function formatDateTime(iso: string): string {
  return serverTime(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatStars(rating: number): string {
  const rounded = Math.round(rating)
  return '★'.repeat(rounded) + '☆'.repeat(5 - rounded)
}
