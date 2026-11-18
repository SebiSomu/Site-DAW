import { describe, expect, it, vi } from 'vitest'
import { ApiError } from './api/client'
import { isRefundedOnCancel, isSafeCheckoutUrl, orderIdFrom, paymentOutcome, waitForPayment } from './payment'

const ORIGIN = 'https://jams.example'

function order(code: string) {
  return { id: 7, status: { code, name: code } }
}

function sequence<T>(...steps: Array<T | Error>) {
  let index = 0
  return vi.fn(async () => {
    const step = steps[Math.min(index++, steps.length - 1)]
    if (step instanceof Error) throw step
    return step
  })
}

const noWait = () => Promise.resolve()

describe('paymentOutcome', () => {
  it('treats an order awaiting payment as pending', () => {
    expect(paymentOutcome({ code: 'pending_payment' })).toBe('pending')
  })

  it('treats a cancelled order as cancelled', () => {
    expect(paymentOutcome({ code: 'cancelled' })).toBe('cancelled')
  })

  it.each(['paid', 'confirmed', 'shipped', 'delivered'])('treats %s as paid', (code) => {
    expect(paymentOutcome({ code })).toBe('paid')
  })

  it('only promises a refund for an order that was paid', () => {
    expect(isRefundedOnCancel({ code: 'paid' })).toBe(true)
    expect(isRefundedOnCancel({ code: 'pending_payment' })).toBe(false)
  })
})

describe('waitForPayment', () => {
  it('stops as soon as the webhook has marked the order paid', async () => {
    const load = sequence(order('pending_payment'), order('pending_payment'), order('paid'))
    const wait = vi.fn(noWait)

    const result = await waitForPayment(load, { attempts: 10, wait })

    expect(result?.outcome).toBe('paid')
    expect(load).toHaveBeenCalledTimes(3)
    expect(wait).toHaveBeenCalledTimes(2)
  })

  it('reports a cancelled order, for a jar that sold out during payment', async () => {
    const result = await waitForPayment(sequence(order('cancelled')), { wait: noWait })

    expect(result?.outcome).toBe('cancelled')
  })

  it('gives up after the last attempt and says the payment is still pending', async () => {
    const load = sequence(order('pending_payment'))
    const wait = vi.fn(noWait)

    const result = await waitForPayment(load, { attempts: 4, wait })

    expect(result?.outcome).toBe('pending')
    expect(load).toHaveBeenCalledTimes(4)
    expect(wait).toHaveBeenCalledTimes(3)
  })

  it('waits the given interval between reads', async () => {
    const wait = vi.fn(noWait)

    await waitForPayment(sequence(order('pending_payment'), order('paid')), { intervalMs: 1500, wait })

    expect(wait).toHaveBeenCalledWith(1500)
  })

  it('keeps trying through a dropped connection', async () => {
    const load = sequence<ReturnType<typeof order>>(new ApiError('offline', 0), order('paid'))

    const result = await waitForPayment(load, { wait: noWait })

    expect(result?.outcome).toBe('paid')
  })

  it('stops at once when the order is not the client’s', async () => {
    const load = sequence<ReturnType<typeof order>>(new ApiError('We could not find this order.', 404), order('paid'))

    await expect(waitForPayment(load, { wait: noWait })).rejects.toThrow('We could not find this order.')
    expect(load).toHaveBeenCalledTimes(1)
  })

  it('passes the error on when no read ever worked', async () => {
    const load = sequence<ReturnType<typeof order>>(new ApiError('offline', 0))

    await expect(waitForPayment(load, { attempts: 3, wait: noWait })).rejects.toThrow('offline')
  })

  it('stops reading once the page has been left', async () => {
    const controller = new AbortController()
    const load = sequence(order('pending_payment'))
    const wait = vi.fn(async () => controller.abort())

    const result = await waitForPayment(load, { attempts: 10, wait, signal: controller.signal })

    expect(load).toHaveBeenCalledTimes(1)
    expect(result?.outcome).toBe('pending')
  })
})

describe('isSafeCheckoutUrl', () => {
  it('accepts Stripe Checkout', () => {
    expect(isSafeCheckoutUrl('https://checkout.stripe.com/c/pay/cs_test_123', ORIGIN)).toBe(true)
  })

  it('accepts a page on this site', () => {
    expect(isSafeCheckoutUrl(`${ORIGIN}/checkout/success?order=7`, ORIGIN)).toBe(true)
  })

  it.each([
    'http://checkout.stripe.com/c/pay/cs_test_123',
    'https://checkout.stripe.com.evil.example/pay',
    'https://evil.example/checkout',
    'javascript:alert(1)',
  ])('refuses %s', (url) => {
    expect(isSafeCheckoutUrl(url, ORIGIN)).toBe(false)
  })
})

describe('orderIdFrom', () => {
  it('reads a plain order number', () => {
    expect(orderIdFrom('42')).toBe(42)
  })

  it.each([null, '', '0', '-3', '4.2', '7abc', '12345678901'])('refuses %s', (value) => {
    expect(orderIdFrom(value)).toBeNull()
  })
})
