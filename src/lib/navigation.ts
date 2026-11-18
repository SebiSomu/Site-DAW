export interface NavLink {
  href: string
  label: string
}

export type CurrentState = 'page' | 'true' | undefined

export function mainNavLinks(isLoggedIn: boolean): NavLink[] {
  return [
    { href: '/about', label: 'About us' },
    { href: '/products', label: 'All jars' },
    isLoggedIn ? { href: '/account', label: 'My account' } : { href: '/login', label: 'Log in' },
  ]
}

export function currentState(href: string, pathname: string): CurrentState {
  if (pathname === href) return 'page'
  if (pathname.startsWith(`${href}/`)) return 'true'
  return undefined
}
