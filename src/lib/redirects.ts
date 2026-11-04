const HOME = '/'

export function safeNextPath(next: string | null): string {
  if (!next || !next.startsWith('/') || next.startsWith('//') || next.startsWith('/\\')) return HOME
  return next
}

export function loginHref(next: string): string {
  return `/login?next=${encodeURIComponent(next)}`
}
