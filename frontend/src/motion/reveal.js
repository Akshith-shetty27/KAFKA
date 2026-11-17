import { gsap, prefersReducedMotion } from './gsap'

/**
 * v-reveal — fade/rise an element in the first time it scrolls into view.
 *
 *   <section v-reveal>…</section>
 *   <li v-for="(x, i) in items" v-reveal="{ delay: i * 0.05 }">…</li>
 *
 * Uses one shared IntersectionObserver (no scroll listeners). Content is never
 * hidden with reduced motion or without IntersectionObserver support, and
 * elements already on screen at mount animate immediately.
 */
let observer = null
const pending = new WeakMap()

function getObserver() {
  if (!observer) {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          observer.unobserve(entry.target)
          pending.get(entry.target)?.()
          pending.delete(entry.target)
        }
      },
      { rootMargin: '0px 0px -8% 0px' },
    )
  }
  return observer
}

export const reveal = {
  mounted(el, binding) {
    if (prefersReducedMotion() || typeof IntersectionObserver === 'undefined') return
    const { delay = 0, y = 18 } = binding.value ?? {}
    // Hide now (a paused `from` tween doesn't render its start state), then
    // animate to the natural state when the element first becomes visible.
    gsap.set(el, { opacity: 0, y })
    pending.set(el, () => {
      el._kReveal = gsap.to(el, { opacity: 1, y: 0, duration: 0.7, delay, clearProps: 'opacity,transform' })
    })
    getObserver().observe(el)
  },
  unmounted(el) {
    observer?.unobserve(el)
    pending.delete(el)
    el._kReveal?.kill()
    delete el._kReveal
  },
}
