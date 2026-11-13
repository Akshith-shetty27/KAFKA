/**
 * Who is signed in.
 *
 * The access token lives only in this store's memory — never in
 * localStorage — so injected scripts can't read it. After a page reload the
 * store is empty, and `init()` silently asks the backend for a new access
 * token using the httpOnly refresh cookie.
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/services/auth.api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(null)
  /** 'unknown' until init() has run, then 'authenticated' | 'anonymous' */
  const status = ref('unknown')
  let initPromise = null

  const isAuthenticated = computed(() => status.value === 'authenticated')
  const theme = computed(() => user.value?.profile?.theme ?? 'ink')
  const displayName = computed(() => user.value?.first_name || user.value?.email?.split('@')[0] || '')

  function setSession({ access, user: nextUser }) {
    accessToken.value = access
    if (nextUser) user.value = nextUser
    status.value = 'authenticated'
  }

  function clearSession() {
    accessToken.value = null
    user.value = null
    status.value = 'anonymous'
  }

  /** Used by the Axios interceptor on 401. Throws if the session is gone. */
  async function refreshAccessToken() {
    const { access } = await authApi.refresh()
    accessToken.value = access
    return access
  }

  /** Restore the session once per page load. Safe to call repeatedly. */
  function init() {
    initPromise ??= (async () => {
      try {
        await refreshAccessToken()
        user.value = await authApi.me()
        status.value = 'authenticated'
      } catch {
        clearSession()
      }
    })()
    return initPromise
  }

  async function login(credentials) {
    setSession(await authApi.login(credentials))
  }

  async function register(payload) {
    setSession(await authApi.register(payload))
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  async function updateMe(patch) {
    user.value = await authApi.updateMe(patch)
    return user.value
  }

  async function changePassword(payload) {
    setSession(await authApi.changePassword(payload))
  }

  return {
    user,
    accessToken,
    status,
    isAuthenticated,
    theme,
    displayName,
    init,
    login,
    register,
    logout,
    updateMe,
    changePassword,
    refreshAccessToken,
    clearSession,
  }
})
