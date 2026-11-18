import { describe, expect, it } from 'vitest'
import { jarPhoto } from './jars'

const PHOTO_SLUGS = [
  'apricot-jam',
  'strawberry-jam',
  'raspberry-jam',
  'wild-blueberry-jam',
  'blackcurrant-jam',
  'sour-cherry-preserve',
  'quince-preserve',
  'rose-petal-preserve',
  'green-walnut-preserve',
  'plum-butter',
  'apple-butter-with-cinnamon',
  'fig-and-walnut-jam',
  'rosehip-jam',
  'peach-jam',
  'cherry-plum-jam',
  'forest-fruit-jam',
  'pear-and-vanilla-butter',
  'lingonberry-jam',
  'orange-marmalade',
  'lemon-and-ginger-marmalade',
]

describe('jarPhoto', () => {
  it('gives the apricot jam its photo in two sizes', () => {
    const photo = jarPhoto({ slug: 'apricot-jam' })

    expect(photo?.src).toBe('/images/jars/apricot.webp')
    expect(photo?.srcset).toContain('/images/jars/apricot-512.webp 512w')
    expect(photo?.alt).toMatch(/^Illustrative photo of /)
  })

  it.each(PHOTO_SLUGS)('gives %s its own photo in two sizes', (slug) => {
    const photo = jarPhoto({ slug })

    expect(photo?.src).toMatch(/^\/images\/jars\/[a-z-]+\.webp$/)
    expect(photo?.srcset).toContain('512w')
    expect(photo?.alt).toMatch(/^Illustrative photo of /)
  })

  it('uses a different file for every jar', () => {
    const files = PHOTO_SLUGS.map((slug) => jarPhoto({ slug })?.src)

    expect(new Set(files).size).toBe(PHOTO_SLUGS.length)
  })

  it('leaves a jar without a photo to its drawing', () => {
    expect(jarPhoto({ slug: 'a-jar-nobody-photographed' })).toBeNull()
  })
})
