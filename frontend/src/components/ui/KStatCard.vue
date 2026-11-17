<script setup>
/** Big italic serif numeral that counts up, a mono label and an optional hint ("07 DAY STREAK"). */
import KCountUp from './KCountUp.vue'

defineProps({
  value: { type: Number, default: null },
  label: { type: String, required: true },
  hint: { type: String, default: '' },
  format: { type: Function, default: (n) => String(n) },
  decimals: { type: Number, default: 0 },
  accent: { type: Boolean, default: false },
})
</script>

<template>
  <div class="flex flex-col gap-3">
    <span class="k-serif text-[3.25rem] leading-none sm:text-6xl" :class="accent ? 'text-accent-text' : 'text-fg'">
      <KCountUp :value="value" :format="format" :decimals="decimals" />
    </span>
    <span class="k-eyebrow text-muted">{{ label }}</span>
    <span v-if="hint" class="text-sm text-muted">{{ hint }}</span>
  </div>
</template>
