<script setup>
/**
 * The sign-in panel's greeting, "letter cascade" style: each letter flies in
 * from blurred to sharp, one after another, then a teal brush-stroke underline
 * draws itself beneath. Re-key the component (e.g. by its text) to replay it.
 * With reduced motion the global rule cuts the animations short, so the text
 * and underline simply appear.
 */
import { computed } from 'vue'

const props = defineProps({
  /** The greeting, without its closing "!" (that's added in teal). */
  text: { type: String, required: true },
})

const STAGGER = 0.05 // seconds between letters
const letters = computed(() => [...props.text, '!'])
// The underline starts drawing as the last letter lands.
const lineDelay = computed(() => `${letters.value.length * STAGGER + 0.35}s`)
</script>

<template>
  <div class="inline-block">
    <p class="k-serif text-6xl leading-none xl:text-7xl">
      <span
        v-for="(ch, i) in letters"
        :key="i"
        class="cascade-letter"
        :class="{ 'text-accent': i === letters.length - 1 }"
        :style="{ animationDelay: `${i * STAGGER}s` }"
        >{{ ch === ' ' ? ' ' : ch }}</span
      >
    </p>
    <svg class="mt-1 block h-4 w-full" viewBox="0 0 250 16" preserveAspectRatio="none" aria-hidden="true">
      <path
        class="cascade-line"
        :style="{ animationDelay: lineDelay }"
        d="M4 10 C 60 2, 120 16, 180 7 S 240 6, 246 9"
        pathLength="1"
        fill="none"
        stroke="currentColor"
        stroke-width="3"
        stroke-linecap="round"
      />
    </svg>
  </div>
</template>

<style scoped>
.cascade-letter {
  display: inline-block;
  animation: cascade-in 700ms cubic-bezier(0.2, 0.9, 0.3, 1.2) both;
}
@keyframes cascade-in {
  from {
    opacity: 0;
    transform: translateX(-18px) rotate(-8deg);
    filter: blur(6px);
  }
}
.cascade-line {
  color: var(--color-accent);
  stroke-dasharray: 1;
  stroke-dashoffset: 1; /* pathLength=1: the dash always spans the whole line */
  animation: cascade-draw 900ms ease-out forwards;
}
@keyframes cascade-draw {
  to {
    stroke-dashoffset: 0;
  }
}
</style>
