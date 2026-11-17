import { reactive } from 'vue'

/**
 * App-wide notifications. Any component can call:
 *
 *   const toast = useToast()
 *   toast.success('Study plan deleted')
 *   toast.error('Could not save — try again')
 *
 * Rendered once by <KToaster> (mounted in App.vue).
 */
const state = reactive({ items: [] })
let nextId = 1
const timers = new Map()

function dismiss(id) {
  clearTimeout(timers.get(id))
  timers.delete(id)
  const i = state.items.findIndex((t) => t.id === id)
  if (i !== -1) state.items.splice(i, 1)
}

function schedule(toast) {
  clearTimeout(timers.get(toast.id))
  timers.set(toast.id, setTimeout(() => dismiss(toast.id), toast.timeout))
}

function push(kind, message, { timeout } = {}) {
  const toast = { id: nextId++, kind, message, timeout: timeout ?? (kind === 'error' ? 7000 : 4000) }
  state.items.push(toast)
  if (state.items.length > 4) dismiss(state.items[0].id)
  schedule(toast)
  return toast.id
}

/** Hovering or focusing a toast pauses its timer; leaving restarts it. */
function pause(id) {
  clearTimeout(timers.get(id))
}
function resume(id) {
  const toast = state.items.find((t) => t.id === id)
  if (toast) schedule(toast)
}

export function useToast() {
  return {
    items: state.items,
    success: (message, options) => push('success', message, options),
    error: (message, options) => push('error', message, options),
    info: (message, options) => push('info', message, options),
    dismiss,
    pause,
    resume,
  }
}
