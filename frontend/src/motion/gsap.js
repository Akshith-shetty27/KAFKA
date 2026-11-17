/**
 * The one place GSAP is configured. Import `gsap` from here, never from 'gsap'
 * directly, so every animation shares the same defaults.
 *
 * ScrollTrigger is *not* part of the app bundle: scroll reveals use the
 * browser's IntersectionObserver (see reveal.js). Pages that need real
 * scroll-linked animation call `loadScrollTrigger()`, which loads and
 * registers the plugin on demand.
 *
 * Motion language (docs/UI-PLAN.md §2): short, eased-out, transform/opacity
 * only, and skipped entirely when the user prefers reduced motion.
 */
import { gsap } from 'gsap'

gsap.defaults({ ease: 'power3.out', duration: 0.6 })

export const REDUCED_MOTION = '(prefers-reduced-motion: reduce)'

export function prefersReducedMotion() {
  return typeof window !== 'undefined' && typeof window.matchMedia === 'function' && window.matchMedia(REDUCED_MOTION).matches
}

let scrollTrigger = null
export async function loadScrollTrigger() {
  if (!scrollTrigger) {
    scrollTrigger = (await import('gsap/ScrollTrigger')).ScrollTrigger
    gsap.registerPlugin(scrollTrigger)
  }
  return scrollTrigger
}

export { gsap }
