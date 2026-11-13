<script setup>
defineProps({
  to: { type: [String, Object], default: '/' },
  size: { type: String, default: 'md' }, // md | lg
})
</script>

<template>
  <RouterLink
    :to="to"
    class="k-display inline-flex items-baseline tracking-[-0.06em] text-fg"
    :class="size === 'lg' ? 'text-5xl' : 'text-[1.75rem]'"
    aria-label="KAFKA home"
  >
    KAFKA<span class="text-accent" aria-hidden="true">.</span>
  </RouterLink>
</template>
