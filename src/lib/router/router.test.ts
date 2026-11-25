import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const ORIGIN = 'https://jams.example'

class FakeElement {
  constructor(private readonly anchor: FakeAnchor | null) {}

  closest(selector: string): FakeAnchor | null {
    return selector === 'a' ? this.anchor : null
  }
}

interface FakeAnchor {
  href: string
  origin: string
  pathname: string
  search: string
  hash: string
  target: string
  hasAttribute(name: string): boolean
}

function anchor(href: string, extra: Partial<FakeAnchor> & { download?: boolean } = {}): FakeAnchor {
  const url = new URL(href, ORIGIN)
  return {
    href: url.href,
    origin: url.origin,
    pathname: url.pathname,
    search: url.search,
    hash: url.hash,
    target: '',
    hasAttribute: (name: string) => name === 'download' && extra.download === true,
    ...extra,
  }
}

function click(target: unknown, extra: Partial<MouseEvent> = {}) {
  const event = {
    defaultPrevented: false,
    button: 0,
    metaKey: false,
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    target,
    preventDefault: vi.fn(),
    ...extra,
  }
  return event
}

let location: URL
let clickHandler: (event: unknown) => void
let popstateHandler: () => void
const history = {
  pushState: vi.fn((_state: unknown, _title: string, url: URL) => {
    location = new URL(url)
  }),
  replaceState: vi.fn((_state: unknown, _title: string, url: URL) => {
    location = new URL(url)
  }),
}
const scrollTo = vi.fn()

async function loadRouter() {
  vi.resetModules()
  return (await import('./router.svelte')).router
}

beforeEach(() => {
  location = new URL('/products', ORIGIN)
  history.pushState.mockClear()
  history.replaceState.mockClear()
  scrollTo.mockClear()
  vi.stubGlobal('Element', FakeElement)
  vi.stubGlobal('window', {
    get location() {
      return { href: location.href, origin: location.origin, pathname: location.pathname, search: location.search }
    },
    history,
    scrollTo,
    addEventListener: (name: string, handler: () => void) => {
      if (name === 'popstate') popstateHandler = handler
    },
  })
  vi.stubGlobal('document', {
    addEventListener: (name: string, handler: (event: unknown) => void) => {
      if (name === 'click') clickHandler = handler
    },
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('router', () => {
  it('starts at the current address', async () => {
    const router = await loadRouter()

    expect(router.url.pathname).toBe('/products')
  })

  it('navigates with pushState and scrolls to the top', async () => {
    const router = await loadRouter()

    router.navigate('/about?tab=story')

    expect(history.pushState).toHaveBeenCalledOnce()
    expect(router.url.pathname).toBe('/about')
    expect(router.url.searchParams.get('tab')).toBe('story')
    expect(scrollTo).toHaveBeenCalledWith(0, 0)
  })

  it('replaces the address without adding a history entry or scrolling', async () => {
    const router = await loadRouter()

    router.replace('/account')

    expect(history.replaceState).toHaveBeenCalledOnce()
    expect(history.pushState).not.toHaveBeenCalled()
    expect(scrollTo).not.toHaveBeenCalled()
    expect(router.url.pathname).toBe('/account')
  })

  it('follows the back button', async () => {
    const router = await loadRouter()
    location = new URL('/cart', ORIGIN)

    popstateHandler()

    expect(router.url.pathname).toBe('/cart')
  })

  it('handles a plain click on an internal link itself', async () => {
    const router = await loadRouter()
    const event = click(new FakeElement(anchor('/products/plum-jam')))

    clickHandler(event)

    expect(event.preventDefault).toHaveBeenCalledOnce()
    expect(router.url.pathname).toBe('/products/plum-jam')
  })

  it.each([
    ['another site', click(new FakeElement(anchor('https://commons.wikimedia.org/wiki/Plums')))],
    ['the API', click(new FakeElement(anchor('/api/health')))],
    ['an uploaded photo', click(new FakeElement(anchor('/uploads/0123456789abcdef0123456789abcdef.webp')))],
    ['a link that opens a new tab', click(new FakeElement(anchor('/about', { target: '_blank' })))],
    ['a download', click(new FakeElement(anchor('/about', { download: true })))],
    ['a jump within the same page', click(new FakeElement(anchor('/products#shelves')))],
    ['a ctrl-click', click(new FakeElement(anchor('/about')), { ctrlKey: true })],
    ['a cmd-click', click(new FakeElement(anchor('/about')), { metaKey: true })],
    ['a shift-click', click(new FakeElement(anchor('/about')), { shiftKey: true })],
    ['an alt-click', click(new FakeElement(anchor('/about')), { altKey: true })],
    ['a middle-click', click(new FakeElement(anchor('/about')), { button: 1 })],
    ['a click already handled', click(new FakeElement(anchor('/about')), { defaultPrevented: true })],
    ['a click outside any link', click(new FakeElement(null))],
    ['a click on a text node', click({})],
  ])('leaves %s to the browser', async (_name, event) => {
    const router = await loadRouter()

    clickHandler(event)

    expect(event.preventDefault).not.toHaveBeenCalled()
    expect(router.url.pathname).toBe('/products')
  })

  it('handles a hash link to another page itself', async () => {
    const router = await loadRouter()
    const event = click(new FakeElement(anchor('/about#faq')))

    clickHandler(event)

    expect(event.preventDefault).toHaveBeenCalledOnce()
    expect(router.url.pathname).toBe('/about')
  })
})
