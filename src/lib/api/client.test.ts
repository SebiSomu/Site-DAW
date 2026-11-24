import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiClient, ApiError, errorMessage, waitText } from './client'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status })
}

function stubFetch(...responses: Response[]) {
  const fetchMock = vi.fn()
  responses.forEach((response) => fetchMock.mockResolvedValueOnce(response))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('ApiClient', () => {
  it('sends the CSRF token with a write and fetches it only once', async () => {
    const fetchMock = stubFetch(jsonResponse({ csrf_token: 'token-1' }), jsonResponse({ ok: 1 }), jsonResponse({ ok: 2 }))
    const client = new ApiClient()

    await client.post('/orders', { address_id: 1 })
    await client.delete('/addresses/1')

    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock.mock.calls[0][0]).toBe('/api/csrf')
    const [url, options] = fetchMock.mock.calls[1]
    expect(url).toBe('/api/orders')
    expect(options.method).toBe('POST')
    expect(options.headers['X-CSRFToken']).toBe('token-1')
    expect(options.body).toBe('{"address_id":1}')
    expect(fetchMock.mock.calls[2][1].method).toBe('DELETE')
  })

  it('adds extra headers to a POST without losing the CSRF token', async () => {
    const fetchMock = stubFetch(jsonResponse({ csrf_token: 'token-1' }), jsonResponse({}))

    await new ApiClient().post('/contact', { name: 'Ana' }, { 'X-Captcha-Token': 'captcha-1' })

    const headers = fetchMock.mock.calls[1][1].headers
    expect(headers['X-Captcha-Token']).toBe('captcha-1')
    expect(headers['X-CSRFToken']).toBe('token-1')
    expect(headers['Content-Type']).toBe('application/json')
  })

  it('sends PUT and PATCH as JSON with the token', async () => {
    const fetchMock = stubFetch(jsonResponse({ csrf_token: 'token-1' }), jsonResponse({}), jsonResponse({}))
    const client = new ApiClient()

    await client.put('/admin/products/1', { stock: 3 })
    await client.patch('/admin/orders/1/status', { status: 'shipped' })

    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: 'PUT', body: '{"stock":3}' })
    expect(fetchMock.mock.calls[2][1]).toMatchObject({ method: 'PATCH', body: '{"status":"shipped"}' })
    expect(fetchMock.mock.calls[2][1].headers['Content-Type']).toBe('application/json')
  })

  it('sends a file upload as form data and lets the browser set its content type', async () => {
    const fetchMock = stubFetch(jsonResponse({ csrf_token: 'token-1' }), jsonResponse({}, 201))
    const form = new FormData()
    form.append('alt_text', 'A jar')

    await new ApiClient().postForm('/admin/products/1/images', form)

    const options = fetchMock.mock.calls[1][1]
    expect(options.body).toBe(form)
    expect(options.headers['X-CSRFToken']).toBe('token-1')
    expect(options.headers['Content-Type']).toBeUndefined()
  })

  it('asks for a new token after the first request for one fails', async () => {
    const fetchMock = stubFetch(jsonResponse({ error: 'down' }, 500), jsonResponse({ csrf_token: 't' }), jsonResponse({}))
    const client = new ApiClient()

    await expect(client.post('/orders')).rejects.toBeInstanceOf(ApiError)
    await client.post('/orders')

    expect(fetchMock.mock.calls[2][1].headers['X-CSRFToken']).toBe('t')
  })

  it('maps an error response to ApiError with the server message and status', async () => {
    stubFetch(jsonResponse({ error: 'Only 2 left of Plum Jam.' }, 409))

    const error = await new ApiClient().get('/products').catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(409)
    expect(errorMessage(error)).toBe('Only 2 left of Plum Jam.')
  })

  it('reports a network failure as status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')))

    const error = await new ApiClient().get('/products').catch((caught: unknown) => caught)

    expect((error as ApiError).status).toBe(0)
  })

  it('accepts an empty 204 response', async () => {
    stubFetch(jsonResponse({ csrf_token: 't' }), new Response(null, { status: 204 }))

    await expect(new ApiClient().delete('/addresses/1')).resolves.toBeNull()
  })

  it('hides unknown errors behind a friendly message', () => {
    expect(errorMessage(new Error('stack details'))).toBe('Something went wrong. Please try again later.')
  })
})

describe('rate limiting', () => {
  it('keeps the server message and reads Retry-After on a 429', async () => {
    const message = 'Too many requests. Please try again in 42 seconds.'
    stubFetch(new Response(JSON.stringify({ error: message }), { status: 429, headers: { 'Retry-After': '42' } }))

    const error = await new ApiClient().get('/products').catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).message).toBe(message)
    expect((error as ApiError).retryAfterSeconds).toBe(42)
    expect((error as ApiError).isRateLimited).toBe(true)
  })

  it('builds the wait message when a 429 has no JSON body', async () => {
    stubFetch(new Response('Too Many Requests', { status: 429, headers: { 'Retry-After': '1' } }))

    const error = (await new ApiClient().get('/products').catch((caught: unknown) => caught)) as ApiError

    expect(error.message).toBe('Too many requests. Please try again in 1 second.')
  })

  it('falls back to "a moment" when Retry-After is missing or a date', async () => {
    stubFetch(new Response('', { status: 429, headers: { 'Retry-After': 'Wed, 21 Oct 2026 07:28:00 GMT' } }))

    const error = (await new ApiClient().get('/products').catch((caught: unknown) => caught)) as ApiError

    expect(error.retryAfterSeconds).toBeNull()
    expect(error.message).toBe('Too many requests. Please try again in a moment.')
  })

  it('has no wait time on other errors', async () => {
    stubFetch(jsonResponse({ error: 'Not found.' }, 404))

    const error = (await new ApiClient().get('/products/x').catch((caught: unknown) => caught)) as ApiError

    expect(error.retryAfterSeconds).toBeNull()
    expect(error.isRateLimited).toBe(false)
  })

  it('words the wait time', () => {
    expect(waitText(1)).toBe('1 second')
    expect(waitText(30)).toBe('30 seconds')
    expect(waitText(null)).toBe('a moment')
  })
})
