import { beforeEach, describe, expect, it, vi } from 'vitest'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))

vi.mock('../api/client', () => ({ api }))

const { AuthStore } = await import('./auth.svelte')

const USER = { id: 3, email: 'ana@example.com', first_name: 'Ana', last_name: 'Pop', role: 'client', is_admin: false }

beforeEach(() => {
  api.get.mockReset()
  api.post.mockReset()
})

describe('AuthStore', () => {
  it('loads the signed-in user and marks itself ready', async () => {
    api.get.mockResolvedValueOnce({ user: USER })
    const auth = new AuthStore()

    expect(auth.ready).toBe(false)
    await auth.load()

    expect(api.get).toHaveBeenCalledWith('/auth/session')
    expect(auth.user).toEqual(USER)
    expect(auth.ready).toBe(true)
  })

  it('treats a failed session check as signed out but still ready', async () => {
    api.get.mockRejectedValueOnce(new Error('offline'))
    const auth = new AuthStore()

    await auth.load()

    expect(auth.user).toBeNull()
    expect(auth.ready).toBe(true)
  })

  it('logs in with the CAPTCHA token in its header', async () => {
    api.post.mockResolvedValueOnce({ user: USER })
    const auth = new AuthStore()

    await auth.login({ email: USER.email, password: 'secret-123' }, 'captcha-1')

    expect(api.post).toHaveBeenCalledWith(
      '/auth/login',
      { email: USER.email, password: 'secret-123' },
      { 'X-Captcha-Token': 'captcha-1' },
    )
    expect(auth.user).toEqual(USER)
  })

  it('registers with the CAPTCHA token in its header', async () => {
    api.post.mockResolvedValueOnce({ user: USER })
    const auth = new AuthStore()
    const details = { email: USER.email, password: 'secret-123', first_name: 'Ana', last_name: 'Pop' }

    await auth.register(details, 'captcha-2')

    expect(api.post).toHaveBeenCalledWith('/auth/register', details, { 'X-Captcha-Token': 'captcha-2' })
    expect(auth.user).toEqual(USER)
  })

  it('keeps the user signed out when login fails', async () => {
    api.post.mockRejectedValueOnce(new Error('Invalid email or password.'))
    const auth = new AuthStore()

    await expect(auth.login({ email: USER.email, password: 'wrong' }, 'captcha-3')).rejects.toThrow('Invalid')
    expect(auth.user).toBeNull()
  })

  it('forgets the user on logout', async () => {
    api.post.mockResolvedValueOnce({ user: USER }).mockResolvedValueOnce(undefined)
    const auth = new AuthStore()
    await auth.login({ email: USER.email, password: 'secret-123' }, 'captcha-4')

    await auth.logout()

    expect(api.post).toHaveBeenLastCalledWith('/auth/logout')
    expect(auth.user).toBeNull()
  })
})
