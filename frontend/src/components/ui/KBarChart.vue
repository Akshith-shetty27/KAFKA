<script setup>
/**
 * Flat teal bars with mono labels underneath — the "THIS WEEK" chart.
 * data: [{ label, value, title? }]. Zero values keep a 2px stub so the
 * baseline reads as a week, not as missing data.
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { whenVisible } from '@/motion/whenVisible'

const props = defineProps({
  data: { type: Array, required: true },
  height: { type: Number, default: 132 },
  /** Accessible summary, e.g. "Questions per day this week" */
  label: { type: String, required: true },
  highlightLast: { type: Boolean, default: false },
})

const max = computed(() => Math.max(1, ...props.data.map((d) => d.value)))
// Bars grow from the baseline the first time the chart is on screen.
const root = ref(null)
const grown = ref(false)
let cancel = () => {}
onMounted(() => {
  cancel = whenVisible(root.value, () => (grown.value = true))
})
onBeforeUnmount(() => cancel())

const summary = computed(() => `${props.label}: ${props.data.map((d) => `${d.title ?? d.label} ${d.value}`).join(', ')}`)
</script>

<template>
  <figure ref="root" :aria-label="summary" role="img">
    <div class="flex items-end gap-1.5 sm:gap-2" :style="{ height: `${height}px` }">
      <div
        v-for="(d, i) in data"
        :key="i"
        class="flex-1 transition-[height] duration-700 ease-[var(--ease-out-soft)]"
        :class="[
          d.value === 0 ? 'bg-rule' : 'bg-accent',
          highlightLast && i === data.length - 1 && d.value > 0 ? 'outline outline-1 outline-offset-2 outline-accent' : '',
        ]"
        :style="{ height: d.value === 0 || !grown ? '2px' : `${Math.max(6, (d.value / max) * 100)}%`, transitionDelay: `${i * 40}ms` }"
        :title="`${d.title ?? d.label}: ${d.value}`"
      />
    </div>
    <div class="mt-3 flex gap-1.5 sm:gap-2" aria-hidden="true">
      <span v-for="(d, i) in data" :key="i" class="k-eyebrow flex-1 text-center tracking-normal text-muted">
        {{ d.label }}
      </span>
    </div>
  </figure>
</template>
