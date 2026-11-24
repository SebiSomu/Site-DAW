import type { QueryParams } from './types'

const UNREACHABLE = 'We could not reach the shop. Check your connection and try again.'
const UNEXPECTED = 'Something went wrong. Please try again later.'
const TOO_MANY_REQUESTS = 429

export function waitText(seconds: number | null): string {
  if (seconds === null) return 'a moment'
  return seconds === 1 ? '1 second' : `${seconds} seconds`
}

function parseRetryAfter(header: string | null): number | null {
  if (header === null || !/^\d+$/.test(header.trim())) return null
  return Math.max(1, Number(header))
}

function failureMessage(status: number, error: unknown, retryAfterSeconds: number | null): string {
  if (typeof error === 'string' && error) return error
  if (status === TOO_MANY_REQUESTS) return `Too many requests. Please try again in ${waitText(retryAfterSeconds)}.`
  return UNEXPECTED
}

export class ApiError extends Error {
  readonly status: number
  readonly retryAfterSeconds: number | null

  constructor(message: string, status: number, retryAfterSeconds: number | null = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.retryAfterSeconds = retryAfterSeconds
  }

  get isRateLimited(): boolean {
    return this.status === TOO_MANY_REQUESTS
  }
}

export class ApiClient {
  private readonly baseUrl: string
  private csrfToken: Promise<string> | null = null

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl
  }

  get<T>(path: string, params: QueryParams = {}): Promise<T> {
    const query = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== '') query.set(key, String(value))
    }
    const search = query.toString()
    return this.request<T>(search ? `${path}?${search}` : path)
  }

  post<T = unknown>(path: string, body?: unknown): Promise<T> {
    return this.write<T>('POST', path, body)
  }

  put<T = unknown>(path: string, body?: unknown): Promise<T> {
    return this.write<T>('PUT', path, body)
  }

  patch<T = unknown>(path: string, body?: unknown): Promise<T> {
    return this.write<T>('PATCH', path, body)
  }

  delete<T = unknown>(path: string): Promise<T> {
    return this.write<T>('DELETE', path)
  }

  postForm<T = unknown>(path: string, form: FormData): Promise<T> {
    return this.send<T>('POST', path, form)
  }

  private write<T>(method: string, path: string, body?: unknown): Promise<T> {
    const json = body === undefined ? undefined : JSON.stringify(body)
    return this.send<T>(method, path, json, { 'Content-Type': 'application/json' })
  }

  private async send<T>(method: string, path: string, body?: string | FormData, headers: Record<string, string> = {}): Promise<T> {
    const token = await this.fetchCsrfToken()
    return this.request<T>(path, { method, headers: { ...headers, 'X-CSRFToken': token }, body })
  }

  private fetchCsrfToken(): Promise<string> {
    this.csrfToken ??= this.request<{ csrf_token: string }>('/csrf')
      .then((body) => body.csrf_token)
      .catch((caught: unknown) => {
        this.csrfToken = null
        throw caught
      })
    return this.csrfToken
  }

  private async request<T>(
    path: string,
    init: { method?: string; headers?: Record<string, string>; body?: string | FormData } = {},
  ): Promise<T> {
    let response: Response
    try {
      response = await fetch(this.baseUrl + path, {
        ...init,
        credentials: 'same-origin',
        headers: { Accept: 'application/json', ...init.headers },
      })
    } catch {
      throw new ApiError(UNREACHABLE, 0)
    }
    const body = await response.json().catch(() => null)
    if (!response.ok) {
      const retryAfter = parseRetryAfter(response.headers.get('Retry-After'))
      throw new ApiError(failureMessage(response.status, body?.error, retryAfter), response.status, retryAfter)
    }
    return body as T
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : UNEXPECTED
}

export const api = new ApiClient()
