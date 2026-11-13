<script setup>
/** Big italic serif numeral + mono label ("07 DAY STREAK"). */
defineProps({
  value: { type: [String, Number], required: true },
  label: { type: String, required: true },
  hint: { type: String, default: '' },
  accent: { type: Boolean, default: false },
})
</script>

<template>
  <div class="flex flex-col gap-3">
    <span class="k-serif text-[3.25rem] leading-none sm:text-6xl" :class="accent ? 'text-accent-text' : 'text-fg'">
      {{ value }}
    </span>
    <span class="k-eyebrow text-muted">{{ label }}</span>
    <span v-if="hint" class="text-sm text-muted">{{ hint }}</span>
  </div>
</template>
