import { onBeforeUnmount, onMounted, watch } from 'vue'

import { gsap, REDUCED_MOTION } from './gsap'

/**
 * Scoped, self-cleaning GSAP animations for a component.
 *
 *   const root = ref(null)
 *   useMotion(root, ({ q, reduced }) => {
 *     if (reduced) return
 *     gsap.from(q('.card'), { y: 16, opacity: 0, stagger: 0.05 })
 *   }, { watch: () => data.value })
 *
 * - `setup` runs after mount inside gsap.matchMedia(), scoped to `root`
 *   (`q` is a selector limited to that element).
 * - Everything it creates — tweens, timelines, ScrollTriggers — is reverted on
 *   unmount, so navigating away never leaves animations or listeners behind.
 * - `reduced` is true when the user prefers reduced motion; GSAP re-runs setup
 *   automatically if that preference changes.
 * - Don't tween `transform` on elements that also have a CSS transform
 *   transition (e.g. `k-lift`): GSAP would read a mid-transition value as the
 *   end state. Animate a wrapper element instead.
 * - `watch`: re-run setup (after reverting the previous run) when the source
 *   changes — for content that arrives after mount, such as API data.
 *   Setup is skipped while the source is null/undefined.
 */
export function useMotion(root, setup, { watch: source } = {}) {
  let mm = null

  function run() {
    mm?.revert()
    mm = null
    const el = root.value?.$el ?? root.value
    if (!el) return
    if (source && source() == null) return
    mm = gsap.matchMedia()
    mm.add(
      { reduced: REDUCED_MOTION, motion: '(prefers-reduced-motion: no-preference)' },
      (context) => setup({ q: gsap.utils.selector(el), el, reduced: context.conditions.reduced, gsap }),
      el,
    )
  }

  onMounted(run)
  if (source) watch(source, run, { flush: 'post' })
  onBeforeUnmount(() => {
    mm?.revert()
    mm = null
  })
}
