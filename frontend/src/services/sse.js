/**
 * POST a JSON body and consume a Server-Sent Events response.
 *
 * Why not Axios: in the browser Axios uses XMLHttpRequest, which can't hand
 * us the body as it streams. `fetch` exposes a ReadableStream instead.
 * Auth matches the Axios client: bearer token from the store, one silent
 * refresh on 401, session-expired handling if that fails.
 *
 * Each `data:` frame is JSON; `onEvent` receives the parsed object.
 * Non-2xx responses (validation errors, 429, …) reject with the API's error
 * shape `{ status, code, message, fields }`.
 */
import { authHandlers, refreshOnce } from './http'

const BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

async function apiErrorFrom(response) {
  let body = null
  try {
    body = await response.json()
  } catch {
    /* non-JSON body */
  }
  const err = body?.error
  return {
    status: response.status,
    code: err?.code ?? 'http_error',
    message: err?.message ?? (response.status === 429 ? 'Too many messages — wait a moment and try again.' : `Request failed (${response.status}).`),
    fields: err?.fields ?? null,
  }
}

async function post(path, body, signal) {
  const token = authHandlers()?.getToken()
  return fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    credentials: 'include',
    signal,
  })
}

export async function postEventStream(path, body, { onEvent, signal } = {}) {
  let response
  try {
    response = await post(path, body, signal)
    if (response.status === 401 && authHandlers()) {
      try {
        await refreshOnce()
      } catch {
        authHandlers().onSessionExpired()
        throw { status: 401, code: 'session_expired', message: 'Your session has expired.', fields: null }
      }
      response = await post(path, body, signal)
    }
  } catch (err) {
    if (err?.name === 'AbortError' || err?.status) throw err
    throw { status: 0, code: 'network_error', message: 'Could not reach the server.', fields: null }
  }

  if (!response.ok) throw await apiErrorFrom(response)

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let boundary
    while ((boundary = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, boundary)
      buffer = buffer.slice(boundary + 2)
      const data = frame
        .split('\n')
        .filter((line) => line.startsWith('data:'))
        .map((line) => line.slice(5).trimStart())
        .join('\n')
      if (data) onEvent?.(JSON.parse(data))
    }
  }
}
