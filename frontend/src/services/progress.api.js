import { http } from './http'

export const progressApi = {
  /** { totals, answers, streak, categories[] } */
  async summary() {
    const { data } = await http.get('/progress/summary/')
    return data
  },
  /** { days, series: [{ date, questions, completed, answered, ai_messages }] } */
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
}
