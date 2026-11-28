import { http } from './http'
import { postEventStream } from './sse'

export const assistantApi = {
  /** { provider, model, offline } */
  async status() {
    const { data } = await http.get('/assistant/status/')
    return data
  },
  /** Paginated: { count, next, previous, results: [{ id, title, question, updated_at, last_message }] } */
  async list(params = {}) {
    const { data } = await http.get('/assistant/conversations/', { params })
    return data
  },
  /** → conversation detail with messages + capabilities */
  /** Start a conversation, optionally about a question, or with a title (e.g. a mock interview). */
  async create(questionSlug, { title } = {}) {
    const body = questionSlug ? { question_slug: questionSlug } : title ? { title } : {}
    const { data } = await http.post('/assistant/conversations/', body)
    return data
  },
  async get(id) {
    const { data } = await http.get(`/assistant/conversations/${id}/`)
    return data
  },
  async remove(id) {
    await http.delete(`/assistant/conversations/${id}/`)
  },
  /**
   * Send a message and stream the reply.
   * payload: { content, mode: 'chat'|'hint'|'explain'|'review', hint_level? }
   * Events: start → token… → done | error
   */
  send(id, payload, { onEvent, signal }) {
    return postEventStream(`/assistant/conversations/${id}/messages/`, payload, { onEvent, signal })
  },
}
