import { reactive, ref } from 'vue'

import { toApiError } from '@/services/http'

/**
 * Submit handling shared by every form: a `submitting` flag, a form-level
 * error message, and per-field errors mapped from the API's
 * `{ error: { message, fields } }` shape (nested objects stay nested, e.g.
 * `fieldErrors.profile.daily_goal`).
 */
export function useForm() {
  const submitting = ref(false)
  const formError = ref('')
  const fieldErrors = reactive({})

  function reset() {
    formError.value = ''
    for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
  }

  async function submit(action) {
    if (submitting.value) return false
    reset()
    submitting.value = true
    try {
      await action()
      return true
    } catch (error) {
      const apiError = error.apiError ?? toApiError(error)
      if (apiError.fields) Object.assign(fieldErrors, apiError.fields)
      // A field error already explains itself next to the field.
      formError.value = apiError.fields && apiError.code === 'validation_error' ? '' : apiError.message
      return false
    } finally {
      submitting.value = false
    }
  }

  return { submitting, formError, fieldErrors, submit, reset }
}
