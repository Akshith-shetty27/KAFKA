/**
 * Call `callback` once, the first time `el` is on screen — one shared
 * IntersectionObserver for the whole app. Without IntersectionObserver the
 * callback runs immediately. Returns a function that cancels the wait.
 *
 * Used by progress bars, rings and charts so their sweep plays when the
 * student can actually see it, not while the panel is still below the fold.
 * (Their real values are always in the DOM/ARIA attributes regardless.)
 */
let observer = null
const callbacks = new WeakMap()

export function whenVisible(el, callback) {
  if (!el || typeof IntersectionObserver === 'undefined') {
    callback()
    return () => {}
  }
  if (!observer) {
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue
        observer.unobserve(entry.target)
        callbacks.get(entry.target)?.()
        callbacks.delete(entry.target)
      }
    })
  }
  callbacks.set(el, callback)
  observer.observe(el)
  return () => {
    observer.unobserve(el)
    callbacks.delete(el)
  }
}
