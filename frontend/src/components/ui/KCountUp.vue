<script setup>
/**
 * A number that counts up to its (real) value when data arrives or changes.
 * Screen readers get the final value only, never the intermediate frames.
 * With reduced motion the value is shown immediately (see useCountUp).
 */
import { useCountUp } from '@/motion'

const props = defineProps({
  value: { type: Number, default: null },
  /** (number) => string, e.g. pad2 or percent */
  format: { type: Function, default: (n) => String(n) },
  decimals: { type: Number, default: 0 },
  fallback: { type: String, default: '—' },
})

const display = useCountUp(() => props.value, { decimals: props.decimals })
</script>

<template>
  <span v-if="value === null || value === undefined">{{ fallback }}</span>
  <span v-else class="tabular-nums"><span aria-hidden="true">{{ format(display) }}</span><span class="sr-only">{{ format(value) }}</span></span>
</template>
