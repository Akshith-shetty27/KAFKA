/**
 * The single Axios instance for the whole app.
 *
 * Every API module (`*.api.js`) imports `http` from here; nothing else in
 * the app talks to Axios directly. Phase 3 adds the auth interceptors
 * (attach access token, refresh on 401) in this file.
 */
import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  withCredentials: true, // send the httpOnly refresh cookie to /auth/*
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Turn any Axios error into the backend's error shape
 * `{ code, message, fields?, status }` so views have one thing to render.
 */
export function toApiError(error) {
  // 502/503/504 without our JSON body = a proxy/gateway couldn't reach Django.
  const isGatewayError = error?.response && error.response.status >= 502 && !error.response.data?.error
  if (error?.response && !isGatewayError) {
    const body = error.response.data?.error
    return {
      status: error.response.status,
      code: body?.code ?? 'http_error',
      message: body?.message ?? `Request failed (${error.response.status}).`,
      fields: body?.fields ?? null,
    }
  }
  if (error?.code === 'ECONNABORTED') {
    return { status: 0, code: 'timeout', message: 'The server took too long to respond.', fields: null }
  }
  return { status: 0, code: 'network_error', message: 'Could not reach the server.', fields: null }
}

http.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(Object.assign(error, { apiError: toApiError(error) })),
)
