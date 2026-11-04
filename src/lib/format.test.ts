import { describe, expect, it } from 'vitest'
import { formatPrice, formatStars } from './format'
import { loginHref, safeNextPath } from './redirects'

describe('formatPrice', () => {
  it.each([
    [2450, '24.50 lei'],
    [100, '1.00 lei'],
    [5, '0.05 lei'],
  ])('shows %i cents as %s', (cents, expected) => {
    expect(formatPrice(cents)).toBe(expected)
  })
})

describe('formatStars', () => {
  it('draws filled and empty stars', () => {
    expect(formatStars(4)).toBe('★★★★☆')
  })
})

describe('safeNextPath', () => {
  it('keeps a path on this site', () => {
    expect(safeNextPath('/checkout?step=1')).toBe('/checkout?step=1')
  })

  it.each([null, '', 'https://evil.example', '//evil.example', '/\\evil.example', 'javascript:alert(1)'])(
    'sends %s back home',
    (next) => {
      expect(safeNextPath(next)).toBe('/')
    },
  )
})

describe('loginHref', () => {
  it('encodes the page to come back to', () => {
    expect(loginHref('/products?q=a b')).toBe('/login?next=%2Fproducts%3Fq%3Da%20b')
  })
})
