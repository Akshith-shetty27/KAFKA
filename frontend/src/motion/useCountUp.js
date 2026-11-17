import { onBeforeUnmount, ref, watch } from 'vue'

import { gsap, prefersReducedMotion } from './gsap'

/**
 * A number that animates towards `source()` whenever it changes (starting from
 * 0 the first time). Returns a ref holding the current displayed value.
 * The real value is always reached; with reduced motion it is set instantly.
 */
export function useCountUp(source, { duration = 0.9, decimals = 0 } = {}) {
  const display = ref(0)
  const state = { value: 0 }
  let tween = null
  const factor = 10 ** decimals

  watch(
    source,
    (target) => {
      tween?.kill()
      if (target == null || Number.isNaN(Number(target))) {
        display.value = target
        return
      }
      if (prefersReducedMotion()) {
        state.value = display.value = Number(target)
        return
      }
      tween = gsap.to(state, {
        value: Number(target),
        duration,
        ease: 'power2.out',
        onUpdate: () => (display.value = Math.round(state.value * factor) / factor),
      })
    },
    { immediate: true },
  )

  onBeforeUnmount(() => tween?.kill())
  return display
}
