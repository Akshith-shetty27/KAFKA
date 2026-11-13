<script setup>
defineProps({
  level: { type: String, required: true }, // easy | medium | hard
})
</script>

<template>
  <span class="k-eyebrow inline-flex items-center gap-2 tracking-[0.2em] text-muted">
    <span
      class="size-1.5 rounded-full"
      :class="{ 'bg-accent': level === 'easy', 'bg-warning': level === 'medium', 'bg-danger': level === 'hard' }"
      aria-hidden="true"
    />
    {{ level }}
  </span>
</template>
