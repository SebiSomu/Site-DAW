import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const api = vi.hoisted(() => ({ post: vi.fn() }))

vi.mock('./api/client', async (importOriginal) => ({ ...(await importOriginal<object>()), api }))

const { startPayment, isSafeCheckoutUrl } = await import('./payment')
const { ApiError } = await import('./api/client')

const ORIGIN = 'https://jams.example'
const assign = vi.fn()

beforeEach(() => {
  api.post.mockReset()
  assign.mockReset()
  vi.stubGlobal('window', { location: { origin: ORIGIN, assign } })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('startPayment', () => {
  it('sends the client to the Stripe Checkout page it was given', async () => {
    api.post.mockResolvedValueOnce({ checkout_url: 'https://checkout.stripe.com/c/pay/cs_test_1' })

    await startPayment(12)

    expect(api.post).toHaveBeenCalledWith('/orders/12/pay')
    expect(assign).toHaveBeenCalledWith('https://checkout.stripe.com/c/pay/cs_test_1')
  })

  it.each([
    'https://checkout.stripe.com.evil.example/c/pay',
    'http://checkout.stripe.com/c/pay',
    'https://evil.example/checkout',
    'javascript:alert(1)',
    '//evil.example/pay',
  ])('refuses to leave the site for %s', async (checkoutUrl) => {
    api.post.mockResolvedValueOnce({ checkout_url: checkoutUrl })

    const error = await startPayment(12).catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as InstanceType<typeof ApiError>).status).toBe(502)
    expect(assign).not.toHaveBeenCalled()
  })

  it('treats an address that cannot be read as unsafe', () => {
    expect(isSafeCheckoutUrl('http://[broken', ORIGIN)).toBe(false)
  })
})
