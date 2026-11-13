import { ref, shallowRef } from 'vue'

import { toApiError } from '@/services/http'

/**
 * Wraps an async function with `data`, `error` and `loading` refs so every
 * view handles loading / error / success the same way.
 *
 *   const { data, error, loading, run } = useAsync(() => systemApi.health())
 *   onMounted(run)
 */
export function useAsync(fn, { initialData = null } = {}) {
  const data = shallowRef(initialData)
  const error = ref(null)
  const loading = ref(false)
  let callId = 0

  async function run(...args) {
    const id = ++callId
    loading.value = true
    error.value = null
    try {
      const result = await fn(...args)
      if (id === callId) data.value = result // ignore results of stale calls
      return result
    } catch (err) {
      if (id === callId) error.value = err.apiError ?? toApiError(err)
      return undefined
    } finally {
      if (id === callId) loading.value = false
    }
  }

  return { data, error, loading, run }
}
