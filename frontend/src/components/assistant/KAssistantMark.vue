<script setup>
/**
 * KAFKA's identity mark: a 3×3 grid of squares whose lit cells draw a "K".
 * While `active` (a reply is being generated) a diagonal wave runs across the
 * grid — the only time it moves. CSS-only; the global reduced-motion rule
 * stops the wave.
 */
defineProps({
  active: { type: Boolean, default: false },
  size: { type: Number, default: 18 },
})

// [row, col] cells of the "K": left column, centre, top-right, bottom-right.
const LIT = new Set(['0,0', '1,0', '2,0', '1,1', '0,2', '2,2'])
const cells = []
for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) cells.push({ r, c, lit: LIT.has(`${r},${c}`) })
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 17 17" class="k-mark shrink-0" :class="{ 'is-active': active }" aria-hidden="true">
    <rect
      v-for="cell in cells"
      :key="`${cell.r}${cell.c}`"
      :x="cell.c * 6"
      :y="cell.r * 6"
      width="5"
      height="5"
      :class="cell.lit ? 'fill-accent' : 'fill-rule'"
      :style="{ '--d': `${(cell.r + cell.c) * 110}ms` }"
    />
  </svg>
</template>

<style scoped>
.k-mark.is-active rect {
  animation: k-mark-wave 1.1s ease-in-out infinite;
  animation-delay: var(--d);
}

@keyframes k-mark-wave {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.2;
  }
}
</style>
