<script setup>
/** Mono section label, e.g. "INTERVIEW PREPARATION". */
defineProps({
  tone: { type: String, default: 'fg' }, // fg | muted | accent
  as: { type: String, default: 'p' },
})
</script>

<template>
  <component
    :is="as"
    class="k-eyebrow"
    :class="{ 'text-fg': tone === 'fg', 'text-muted': tone === 'muted', 'text-accent-text': tone === 'accent' }"
  >
    <slot />
  </component>
</template>
