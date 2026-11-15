import { http } from './http'

/** Study plans generated from a pasted job description (ASK KAFKA). */
export const prepApi = {
  /** Paginated: { count, results: [{ id, role, company, days_available, created_at, progress }] } */
  async list(params = {}) {
    const { data } = await http.get('/prep/plans/', { params })
    return data
  },
  /**
   * payload: { role, job_description, company?, candidate_info?, days_available?, hours_per_day? }
   * One AI call on the server (typically ~10 s), so this gets a longer timeout than other requests.
   */
  async create(payload) {
    const { data } = await http.post('/prep/plans/', payload, { timeout: 90000 })
    return data
  },
  async get(id) {
    const { data } = await http.get(`/prep/plans/${id}/`)
    return data
  },
  async remove(id) {
    await http.delete(`/prep/plans/${id}/`)
  },
  /** → { id, completed, completed_at } */
  async setItemCompleted(planId, itemId, completed) {
    const { data } = await http.patch(`/prep/plans/${planId}/items/${itemId}/`, { completed })
    return data
  },
}
