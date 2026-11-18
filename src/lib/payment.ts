import { ApiError, api } from './api/client'
import type { OrderStatus } from './api/types'

export type PaymentOutcome = 'paid' | 'cancelled' | 'pending'

export const AWAITING_PAYMENT = 'pending_payment'
const CANCELLED = 'cancelled'
const STRIPE_CHECKOUT_HOST = 'checkout.stripe.com'
const PAYMENT_PAGE_UNAVAILABLE = 'We could not open the payment page. Please try again in a moment.'

export interface PollOptions {
  attempts?: number
  intervalMs?: number
  signal?: AbortSignal
  wait?: (milliseconds: number) => Promise<void>
}

export interface PollResult<T> {
  order: T
  outcome: PaymentOutcome
}

export function paymentOutcome(status: Pick<OrderStatus, 'code'>): PaymentOutcome {
  if (status.code === AWAITING_PAYMENT) return 'pending'
  if (status.code === CANCELLED) return 'cancelled'
  return 'paid'
}

export function isRefundedOnCancel(status: Pick<OrderStatus, 'code'>): boolean {
  return paymentOutcome(status) === 'paid'
}

function pause(milliseconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds))
}

function isClientError(error: unknown): boolean {
  return error instanceof ApiError && error.status >= 400 && error.status < 500
}

export async function waitForPayment<T extends { status: Pick<OrderStatus, 'code'> }>(
  load: () => Promise<T>,
  { attempts = 10, intervalMs = 2000, signal, wait = pause }: PollOptions = {},
): Promise<PollResult<T> | null> {
  let latest: PollResult<T> | null = null
  let lastError: unknown = null
  for (let attempt = 1; attempt <= attempts; attempt++) {
    if (signal?.aborted) return latest
    try {
      const order = await load()
      latest = { order, outcome: paymentOutcome(order.status) }
      if (latest.outcome !== 'pending') return latest
    } catch (caught) {
      if (isClientError(caught)) throw caught
      lastError = caught
    }
    if (attempt < attempts) await wait(intervalMs)
  }
  if (!latest && lastError) throw lastError
  return latest
}

export function isSafeCheckoutUrl(candidate: string, origin: string): boolean {
  let url: URL
  try {
    url = new URL(candidate, origin)
  } catch {
    return false
  }
  if (url.origin === origin) return true
  return url.protocol === 'https:' && url.hostname === STRIPE_CHECKOUT_HOST
}

export async function startPayment(orderId: number): Promise<void> {
  const body = await api.post<{ checkout_url: string }>(`/orders/${orderId}/pay`)
  if (!isSafeCheckoutUrl(body.checkout_url, window.location.origin)) {
    throw new ApiError(PAYMENT_PAGE_UNAVAILABLE, 502)
  }
  window.location.assign(body.checkout_url)
}

export function orderIdFrom(value: string | null): number | null {
  return value && /^[1-9][0-9]{0,9}$/.test(value) ? Number(value) : null
}
