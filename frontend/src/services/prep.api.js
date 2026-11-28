import { http } from './http'

/** Study plans generated from a pasted job description (ASK KAFKA). */
export const prepApi = {
  /** Paginated: { count, results: [{ id, role, company, days_available, created_at, progress }] } */
  async list(params = {}) {
    const { data } = await http.get('/prep/plans/', { params })
    return data
  },
  /**
   * payload: { role, job_description, company?, days_available?, hours_per_day? }
   * Web research + one AI call on the server (typically 30–60 s on the free tier),
   * so this gets a much longer timeout than other requests.
   */
  async create(payload) {
    const { data } = await http.post('/prep/plans/', payload, { timeout: 150000 })
    return data
  },
  async get(id) {
    const { data } = await http.get(`/prep/plans/${id}/`)
    return data
  },
  async remove(id) {
    await http.delete(`/prep/plans/${id}/`)
  },
  /**
   * Notes + quiz for a "lesson" item — generated on first request (a few seconds), then stored.
   * → { id, lesson: { sections[{heading, body}], key_points[], quiz[{question, options, answer, explanation}], model } }
   */
  async lesson(planId, itemId) {
    const { data } = await http.post(`/prep/plans/${planId}/items/${itemId}/lesson/`, {}, { timeout: 60000 })
    return data
  },
  /** → { id, completed, completed_at } */
  async setItemCompleted(planId, itemId, completed) {
    const { data } = await http.patch(`/prep/plans/${planId}/items/${itemId}/`, { completed })
    return data
  },
}
