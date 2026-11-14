import { http } from './http'

const q = (slug) => `/questions/${encodeURIComponent(slug)}`

export const progressApi = {
  // --- reads (dashboard / progress page) ------------------------------------------
  /** { totals, answers, streak, categories[] } */
  async summary() {
    const { data } = await http.get('/progress/summary/')
    return data
  },
  /** { days, series: [{ date, questions, completed, answered, ai_messages }] } — days: 7|14|30|90|365 */
  async activity(days = 7) {
    const { data } = await http.get('/progress/activity/', { params: { days } })
    return data
  },
  /** [{ question, status, is_correct, updated_at, completed_at }] */
  async recent(limit = 6) {
    const { data } = await http.get('/progress/recent/', { params: { limit } })
    return data
  },
  /** { date, daily_goal, completed_today, items[], recommended_topics[] } */
  async plan() {
    const { data } = await http.get('/progress/plan/')
    return data
  },
  /** { difficulty[], topics[] (with first-try accuracy), focus_areas[{ reason, topic }] } */
  async insights() {
    const { data } = await http.get('/progress/insights/')
    return data
  },

  // --- writes (question pages) --------------------------------------------------
  /** I opened this question → progress state */
  async attempt(slug) {
    const { data } = await http.post(`${q(slug)}/attempt/`)
    return data
  },
  /** MCQ → { is_correct, correct_option_id, explanation, progress } (graded on the server) */
  async answer(slug, optionId) {
    const { data } = await http.post(`${q(slug)}/answer/`, { option_id: optionId })
    return data
  },
  /** Coding/concept → progress state */
  async complete(slug) {
    const { data } = await http.put(`${q(slug)}/progress/`, { status: 'completed' })
    return data
  },
  /** Forget my progress on this question (history is kept). */
  async reset(slug) {
    await http.delete(`${q(slug)}/progress/`)
  },
}
