<script setup>
/**
 * Circular progress that sweeps to its value on mount and whenever it changes
 * (CSS transition on stroke-dashoffset — no animation loop). Anything in the
 * default slot is centred inside the ring.
 */
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: Number, required: true },
  max: { type: Number, required: true },
  label: { type: String, required: true },
  size: { type: Number, default: 72 },
  stroke: { type: Number, default: 4 },
})

const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const ratio = computed(() => (props.max > 0 ? Math.min(1, Math.max(0, props.value / props.max)) : 0))

// Start empty and sweep in after the first paint.
const shown = ref(0)
onMounted(() => requestAnimationFrame(() => (shown.value = ratio.value)))
watch(ratio, (r) => (shown.value = r))
</script>

<template>
  <div
    class="relative inline-flex shrink-0 items-center justify-center"
    :style="{ width: `${size}px`, height: `${size}px` }"
    role="progressbar"
    :aria-label="label"
    :aria-valuenow="value"
    aria-valuemin="0"
    :aria-valuemax="max"
  >
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" class="-rotate-90" aria-hidden="true">
      <circle :cx="size / 2" :cy="size / 2" :r="radius" fill="none" class="stroke-rule-soft" :stroke-width="stroke" />
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        class="stroke-accent transition-[stroke-dashoffset] duration-1000 ease-[var(--ease-out-soft)]"
        :stroke-width="stroke"
        stroke-linecap="butt"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="circumference * (1 - shown)"
      />
    </svg>
    <div class="absolute inset-0 flex items-center justify-center"><slot /></div>
  </div>
</template>
