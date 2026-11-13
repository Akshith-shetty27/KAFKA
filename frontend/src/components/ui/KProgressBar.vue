<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, required: true },
  max: { type: Number, required: true },
  label: { type: String, required: true },
})

const pct = computed(() => (props.max > 0 ? Math.min(100, (props.value / props.max) * 100) : 0))
</script>

<template>
  <div
    class="h-[3px] w-full bg-rule-soft"
    role="progressbar"
    :aria-label="label"
    :aria-valuenow="value"
    aria-valuemin="0"
    :aria-valuemax="max"
  >
    <div class="h-full bg-accent transition-[width] duration-700 ease-out" :style="{ width: `${pct}%` }" />
  </div>
</template>
