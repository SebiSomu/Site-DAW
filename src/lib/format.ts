export function formatPrice(cents: number): string {
  return `${(cents / 100).toFixed(2)} lei`
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

export function formatStars(rating: number): string {
  const rounded = Math.round(rating)
  return '★'.repeat(rounded) + '☆'.repeat(5 - rounded)
}
