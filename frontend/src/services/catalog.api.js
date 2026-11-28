import { http } from './http'

export const catalogApi = {
  /** [{ slug, name, description, glyph, question_count, attempted_count, completed_count }] */
  /** Public: published question counts per track — { total, tracks: [{ slug, name, count }] }. */
  async stats() {
    const { data } = await http.get('/catalog/stats/')
    return data
  },
  async categories() {
    const { data } = await http.get('/categories/')
    return data
  },
  /** Topics with section and my counts; optionally for one category. */
  async topics(category) {
    const { data } = await http.get('/topics/', { params: category ? { category } : {} })
    return data
  },
  async patterns() {
    const { data } = await http.get('/patterns/')
    return data
  },
  /**
   * Paginated question summaries.
   * params: { category, topic, difficulty, status, pattern, search, page, page_size }
   * → { count, next, previous, results }
   */
  async questions(params) {
    const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v !== null && v !== undefined))
    const { data } = await http.get('/questions/', { params: clean })
    return data
  },
  /** Full question with my progress and prev/next navigation. */
  async question(slug) {
    const { data } = await http.get(`/questions/${encodeURIComponent(slug)}/`)
    return data
  },
}
