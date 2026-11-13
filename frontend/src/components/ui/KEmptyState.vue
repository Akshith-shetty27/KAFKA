<script setup>
defineProps({
  title: { type: String, required: true },
  glyph: { type: String, default: '∅' },
})
</script>

<template>
  <div class="flex flex-col items-start gap-3 border border-dashed border-rule-soft p-6">
    <span class="k-serif text-4xl leading-none text-muted" aria-hidden="true">{{ glyph }}</span>
    <p class="font-medium">{{ title }}</p>
    <p class="text-sm text-muted"><slot /></p>
  </div>
</template>
