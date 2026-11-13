import { http } from './http'

export const systemApi = {
  /** GET /health/ → { status, database } */
  async health() {
    const { data } = await http.get('/health/')
    return data
  },
}
