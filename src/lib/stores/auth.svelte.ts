import { api } from '../api/client'
import type { LoginDetails, RegisterDetails, User } from '../api/types'

export class AuthStore {
  user = $state<User | null>(null)
  ready = $state(false)

  async load(): Promise<void> {
    try {
      const body = await api.get<{ user: User | null }>('/auth/session')
      this.user = body.user
    } catch {
      this.user = null
    } finally {
      this.ready = true
    }
  }

  async login(details: LoginDetails): Promise<void> {
    this.user = (await api.post<{ user: User }>('/auth/login', details)).user
  }

  async register(details: RegisterDetails): Promise<void> {
    this.user = (await api.post<{ user: User }>('/auth/register', details)).user
  }

  async logout(): Promise<void> {
    await api.post('/auth/logout')
    this.user = null
  }
}

export const auth = new AuthStore()
