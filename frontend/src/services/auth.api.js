import { http } from './http'

const publicCall = { skipAuth: true }

export const authApi = {
  /** → { access, user } and sets the refresh cookie */
  async register(payload) {
    const { data } = await http.post('/auth/register/', payload, publicCall)
    return data
  },
  /** → { access, user } and sets the refresh cookie */
  async login(credentials) {
    const { data } = await http.post('/auth/login/', credentials, publicCall)
    return data
  },
  /** Uses the refresh cookie → { access } */
  async refresh() {
    const { data } = await http.post('/auth/refresh/', null, publicCall)
    return data
  },
  async logout() {
    await http.post('/auth/logout/', null, publicCall)
  },
  async me() {
    const { data } = await http.get('/auth/me/')
    return data
  },
  /** Partial update: { first_name?, last_name?, profile?: {...} } */
  async updateMe(patch) {
    const { data } = await http.patch('/auth/me/', patch)
    return data
  },
  /** → { access, user }; other sessions are signed out */
  async changePassword(payload) {
    const { data } = await http.post('/auth/change-password/', payload)
    return data
  },
}
