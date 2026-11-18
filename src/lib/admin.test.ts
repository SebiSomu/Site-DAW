import { describe, expect, it } from 'vitest'
import {
  checkPhoto,
  hrefWithQuery,
  ingredientsFrom,
  MAX_PHOTO_BYTES,
  parseLei,
  positiveInt,
  slugify,
  stepLabel,
  toLeiInput,
} from './admin'

describe('parseLei', () => {
  it.each([
    ['24.50', 2450],
    ['24,50', 2450],
    ['24', 2400],
    [' 24.5 ', 2450],
    ['0.05', 5],
  ])('reads %s as %i bani', (text, cents) => {
    expect(parseLei(text)).toBe(cents)
  })

  it.each(['', '0', '0.00', '-3', '24.505', 'abc', '24.50 lei', '1e3', '123456'])('refuses %s', (text) => {
    expect(parseLei(text)).toBeNull()
  })

  it('writes bani back the way the field shows them', () => {
    expect(toLeiInput(2450)).toBe('24.50')
    expect(parseLei(toLeiInput(3105))).toBe(3105)
  })
})

describe('ingredientsFrom', () => {
  it('splits on commas and lines, tidies and drops repeats', () => {
    expect(ingredientsFrom('Quinces, sugar\n quinces ,, lemon ')).toEqual(['quinces', 'sugar', 'lemon'])
  })
})

describe('slugify', () => {
  it('matches the web address the server makes', () => {
    expect(slugify('Dulceață de Gutui Veche')).toBe('dulceata-de-gutui-veche')
    expect(slugify('  Fig & Walnut Jam!! ')).toBe('fig-walnut-jam')
    expect(slugify('***')).toBe('')
  })
})

describe('checkPhoto', () => {
  it('accepts an ordinary photo', () => {
    expect(checkPhoto({ name: 'Jar.JPG', size: 2_000_000 })).toBeNull()
  })

  it.each([
    [{ name: 'shell.php', size: 10 }, 'Only .jpg'],
    [{ name: 'jar.jpg.php', size: 10 }, 'Only .jpg'],
    [{ name: 'jar', size: 10 }, 'Only .jpg'],
    [{ name: '.png', size: 10 }, 'Only .jpg'],
    [{ name: 'jar.png', size: 0 }, 'empty'],
    [{ name: 'jar.png', size: MAX_PHOTO_BYTES + 1 }, 'larger than 12 MB'],
  ])('refuses %o before it is sent', (file, message) => {
    expect(checkPhoto(file)).toContain(message)
  })

  it('lets a photo of exactly 12 MB through', () => {
    expect(checkPhoto({ name: 'jar.webp', size: MAX_PHOTO_BYTES })).toBeNull()
  })
})

describe('stepLabel', () => {
  it('names each next step for the admin', () => {
    expect(stepLabel('shipped', true)).toBe('Mark as shipped')
    expect(stepLabel('cancelled', true)).toBe('Cancel and refund')
    expect(stepLabel('cancelled', false)).toBe('Cancel order')
  })
})

describe('hrefWithQuery', () => {
  it('keeps only the filters that are set and leaves out page 1', () => {
    expect(hrefWithQuery('/admin/activity-log', { action: 'login', user_id: '', level: undefined, page: 1 })).toBe(
      '/admin/activity-log?action=login',
    )
    expect(hrefWithQuery('/admin/messages', { page: 2 })).toBe('/admin/messages?page=2')
    expect(hrefWithQuery('/admin/orders', {})).toBe('/admin/orders')
  })
})

describe('positiveInt', () => {
  it('reads page numbers and ids from the address bar', () => {
    expect(positiveInt('3')).toBe(3)
    expect(positiveInt('0')).toBeNull()
    expect(positiveInt('2; DROP')).toBeNull()
    expect(positiveInt(null)).toBeNull()
  })
})
