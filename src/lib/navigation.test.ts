import { describe, expect, it } from 'vitest'
import { currentState, mainNavLinks } from './navigation'

describe('mainNavLinks', () => {
  it('offers the story, the whole shelf and logging in to a guest', () => {
    expect(mainNavLinks(false).map((link) => link.label)).toEqual(['About us', 'All jars', 'Log in'])
  })

  it('swaps logging in for the account once logged in', () => {
    expect(mainNavLinks(true).at(-1)).toEqual({ href: '/account', label: 'My account' })
  })

  it('shows the admin link to the admin only', () => {
    expect(mainNavLinks(true).some((link) => link.href === '/admin')).toBe(false)
    expect(mainNavLinks(true, true).map((link) => link.label)).toEqual(['About us', 'All jars', 'Admin', 'My account'])
  })

  it('no longer lists the shelves one by one', () => {
    expect(mainNavLinks(false).some((link) => link.href.includes('category='))).toBe(false)
  })
})

describe('currentState', () => {
  it.each([
    ['/products', '/products', 'page'],
    ['/products', '/products/plum-butter', 'true'],
    ['/account', '/account/orders/3', 'true'],
    ['/about', '/products', undefined],
    ['/account', '/accounts', undefined],
  ])('marks %s on %s as %s', (href, pathname, expected) => {
    expect(currentState(href, pathname)).toBe(expected)
  })
})
