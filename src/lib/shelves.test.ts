import { describe, expect, it } from 'vitest'
import { SEASONS, productHref } from './seasons'
import { SHELVES, shelfHref } from './shelves'

describe('shelves', () => {
  it('links each shelf to the filtered shop', () => {
    expect(shelfHref('fruit-butters')).toBe('/products?category=fruit-butters')
  })

  it('has four shelves, each with a unique address, a picture and a description of it', () => {
    expect(SHELVES).toHaveLength(4)
    expect(new Set(SHELVES.map((shelf) => shelf.slug)).size).toBe(4)
    for (const shelf of SHELVES) {
      expect(shelf.image).toMatch(/^\/images\/plates\/[a-z-]+\.jpg$/)
      expect(shelf.imageAlt.length).toBeGreaterThan(20)
    }
  })
})

describe('seasons', () => {
  it('links a jar to its product page', () => {
    expect(productHref('plum-jam')).toBe('/products/plum-jam')
  })

  it('names every jar it links to', () => {
    const jars = SEASONS.flatMap((season) => season.jars)

    expect(jars.length).toBeGreaterThan(0)
    for (const jar of jars) {
      expect(jar.slug).toMatch(/^[a-z0-9-]+$/)
      expect(jar.name.trim()).not.toBe('')
    }
  })
})
