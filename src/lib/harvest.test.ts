import { describe, expect, it } from 'vitest'
import { harvestLabel, harvestRows, isInSeason, spanLabel } from './harvest'
import { SEASONS } from './seasons'

describe('harvestRows', () => {
  const rows = harvestRows()

  it('has one row per jar the About page says is made', () => {
    const seasonSlugs = SEASONS.flatMap((season) => season.jars.map((jar) => jar.slug)).sort()

    expect(rows.map((row) => row.slug).sort()).toEqual(seasonSlugs)
  })

  it('keeps every month span inside the year and in order', () => {
    for (const row of rows) {
      for (const [first, last] of row.spans) {
        expect(first).toBeGreaterThanOrEqual(1)
        expect(last).toBeLessThanOrEqual(12)
        expect(first).toBeLessThanOrEqual(last)
      }
    }
  })

  it('gives every fruit the colour of its jam', () => {
    for (const row of rows) {
      expect(row.colour).toMatch(/^#[0-9a-f]{6}$/i)
    }
    expect(rows.find((row) => row.slug === 'apricot-jam')?.colour).toBe('#e08a2c')
  })

  it('matches the months written on the season cards', () => {
    const cardMonths: Record<string, number[]> = {
      'late-spring': [5, 6],
      'high-summer': [7, 8],
      autumn: [9, 10],
      'first-frost': [11],
      winter: [12, 1, 2, 3],
    }
    for (const season of SEASONS) {
      for (const jar of season.jars) {
        const row = rows.find((candidate) => candidate.slug === jar.slug)
        const months = cardMonths[season.id]
        expect(months.some((month) => row && isInSeason(row, month))).toBe(true)
      }
    }
  })
})

describe('month labels', () => {
  it('names a single month', () => {
    expect(spanLabel([6, 6])).toBe('June')
  })

  it('names a range', () => {
    expect(spanLabel([7, 8])).toBe('July to August')
  })

  it('joins the two ends of a winter that wraps the year', () => {
    expect(harvestLabel({ spans: [[1, 3], [12, 12]] })).toBe('January to March and December')
  })

  it('knows which months a fruit is in season', () => {
    const row = { spans: [[1, 3], [12, 12]] as [number, number][] }

    expect(isInSeason(row, 2)).toBe(true)
    expect(isInSeason(row, 12)).toBe(true)
    expect(isInSeason(row, 7)).toBe(false)
  })
})
