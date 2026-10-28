import type { QueryParams } from './types'

const UNREACHABLE = 'We could not reach the shop. Check your connection and try again.'
const UNEXPECTED = 'Something went wrong. Please try again later.'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export class ApiClient {
  private readonly baseUrl: string

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

  private async request<T>(path: string): Promise<T> {
    let response: Response
    try {
      response = await fetch(this.baseUrl + path, {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      })
    } catch {
      throw new ApiError(UNREACHABLE, 0)
    }
    const body = await response.json().catch(() => null)
    if (!response.ok) throw new ApiError(body?.error ?? UNEXPECTED, response.status)
    return body as T
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : UNEXPECTED
}

export const api = new ApiClient()
