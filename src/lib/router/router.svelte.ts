const SERVER_PREFIXES = ['/api/', '/uploads/']

class Router {
  url = $state(new URL(window.location.href))

  constructor() {
    window.addEventListener('popstate', () => this.sync())
    document.addEventListener('click', (event) => this.interceptLink(event))
  }

  navigate(href: string): void {
    window.history.pushState(null, '', new URL(href, window.location.origin))
    this.sync()
    window.scrollTo(0, 0)
  }

  private sync(): void {
    this.url = new URL(window.location.href)
  }

  private interceptLink(event: MouseEvent): void {
    if (event.defaultPrevented || event.button !== 0) return
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
    if (!(event.target instanceof Element)) return
    const anchor = event.target.closest('a')
    if (!anchor || anchor.target || anchor.hasAttribute('download')) return
    if (anchor.origin !== window.location.origin) return
    if (SERVER_PREFIXES.some((prefix) => anchor.pathname.startsWith(prefix))) return
    event.preventDefault()
    this.navigate(anchor.href)
  }
}

export const router = new Router()
