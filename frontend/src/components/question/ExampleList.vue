<script setup>
defineProps({
  examples: { type: Array, required: true }, // [{ input, output, explanation }]
})
</script>

<template>
  <ol class="flex flex-col gap-4">
    <li v-for="(ex, i) in examples" :key="i" class="bg-surface p-5">
      <p class="k-eyebrow mb-4 text-muted">Example {{ i + 1 }}</p>
      <dl class="grid grid-cols-[4.5rem_minmax(0,1fr)] gap-x-4 gap-y-2 font-mono text-sm">
        <dt class="text-muted">Input</dt>
        <dd class="break-words">{{ ex.input }}</dd>
        <dt class="text-muted">Output</dt>
        <dd class="break-words font-medium">{{ ex.output }}</dd>
      </dl>
      <p v-if="ex.explanation" class="mt-3 border-t border-rule-soft pt-3 text-sm text-muted">{{ ex.explanation }}</p>
    </li>
  </ol>
</template>
