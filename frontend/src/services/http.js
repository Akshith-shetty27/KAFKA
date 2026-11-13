/**
 * The single Axios instance for the whole app.
 *
 * Every API module (`*.api.js`) imports `http` from here; nothing else talks
 * to Axios directly. Auth is plugged in from outside via `installAuth()` so
 * this file doesn't import the store (which itself imports the API modules).
 *
 * Flow for an expired access token:
 *   request → 401 → one shared refresh call (cookie) → retry the request once
 *   refresh fails → onSessionExpired() (store clears session, router → login)
 *
 * Requests made with `{ skipAuth: true }` (login/register/refresh/logout)
 * never carry the access token and are never retried.
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
 * `{ status, code, message, fields }` so views have one thing to render.
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

let auth = null
let refreshInFlight = null

/** @param {{ getToken: () => string|null, refresh: () => Promise<string>, onSessionExpired: () => void }} handlers */
export function installAuth(handlers) {
  auth = handlers
}

http.interceptors.request.use((config) => {
  const token = auth?.getToken()
  if (token && !config.skipAuth) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const shouldRefresh = response?.status === 401 && auth && config && !config.skipAuth && !config._retried

    if (shouldRefresh) {
      config._retried = true
      try {
        // Many requests can fail at once; they all wait on the same refresh.
        refreshInFlight ??= auth.refresh().finally(() => {
          refreshInFlight = null
        })
        await refreshInFlight
        return http(config)
      } catch {
        auth.onSessionExpired()
      }
    }
    return Promise.reject(Object.assign(error, { apiError: toApiError(error) }))
  },
)
