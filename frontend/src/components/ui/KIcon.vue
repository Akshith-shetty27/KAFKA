<script setup>
/**
 * Minimal line-icon set (24px grid, 1.5 stroke, currentColor). Kept inline so
 * we don't pull in an icon library for a dozen glyphs.
 */
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
})

const paths = {
  'arrow-up-right': ['M7 17 17 7', 'M8 7h9v9'],
  'chevron-right': ['m9 6 6 6-6 6'],
  check: ['M5 12.5 9.5 17 19 7'],
  flame: ['M12 3c.4 3.4 4.6 5.2 4.6 10.2a4.6 4.6 0 0 1-9.2 0c0-2.3 1.2-3.7 2.3-4.7.2 1.7 1 2.7 2.3 3.1.3-2.9-.3-5.7 0-8.6Z'],
  menu: ['M4 7h16', 'M4 12h16', 'M4 17h16'],
  close: ['m6 6 12 12', 'M18 6 6 18'],
  eye: ['M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z', 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z'],
  'eye-off': ['m3 3 18 18', 'M10.6 5.1A10.6 10.6 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4.1', 'M6.6 6.6C3.9 8.4 2 12 2 12s3.6 7 10 7c1.6 0 3-.4 4.3-1', 'M9.9 9.9a3 3 0 0 0 4.2 4.2'],
  refresh: ['M20 11a8 8 0 1 0-2.3 5.7', 'M20 4v7h-7'],
  logout: ['M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3', 'm10 17 5-5-5-5', 'M15 12H3'],
  settings: ['M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M12 2v3', 'M12 19v3', 'm4.9 4.9 2.1 2.1', 'm17 17 2.1 2.1', 'M2 12h3', 'M19 12h3', 'm4.9 19.1 2.1-2.1', 'm17 7 2.1-2.1'],
  alert: ['M12 8v5', 'M12 16.5v.01', 'M10.3 3.9 2.4 17.6A2 2 0 0 0 4.1 20.6h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z'],
}
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.5"
    stroke-linecap="square"
    stroke-linejoin="miter"
    aria-hidden="true"
    focusable="false"
    class="shrink-0"
  >
    <path v-for="d in paths[name]" :key="d" :d="d" />
  </svg>
</template>
