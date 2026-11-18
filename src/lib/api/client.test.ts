import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiClient, ApiError, errorMessage } from './client'

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
