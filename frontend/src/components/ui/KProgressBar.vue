<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { whenVisible } from '@/motion/whenVisible'

const props = defineProps({
  value: { type: Number, required: true },
  max: { type: Number, required: true },
  label: { type: String, required: true },
})

const pct = computed(() => (props.max > 0 ? Math.min(100, (props.value / props.max) * 100) : 0))

// Fill from empty the first time the bar is on screen; later changes animate too.
const root = ref(null)
const shown = ref(0)
let seen = false
let cancel = () => {}
onMounted(() => {
  cancel = whenVisible(root.value, () => {
    seen = true
    shown.value = pct.value // already painted at 0 by now, so the CSS transition runs
  })
})
onBeforeUnmount(() => cancel())
watch(pct, (v) => {
  if (seen) shown.value = v
})
</script>

<template>
  <div
    ref="root"
    class="h-[3px] w-full bg-rule-soft"
    role="progressbar"
    :aria-label="label"
    :aria-valuenow="value"
    aria-valuemin="0"
    :aria-valuemax="max"
  >
    <div class="h-full bg-accent transition-[width] duration-700 ease-out" :style="{ width: `${shown}%` }" />
  </div>
</template>
