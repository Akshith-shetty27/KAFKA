<script setup>
/**
 * The references' primary call to action: tracked uppercase text with an
 * arrow and a 1px underline ("START PREPARING ↗"). Router link when `to` is
 * given, plain anchor for `href`.
 */
import KIcon from './KIcon.vue'

defineProps({
  to: { type: [String, Object], default: null },
  href: { type: String, default: null },
  icon: { type: String, default: 'arrow-up-right' }, // arrow-up-right | chevron-right | none
  underline: { type: Boolean, default: true },
})
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'a'"
    :to="to ?? undefined"
    :href="to ? undefined : href"
    class="group k-label inline-flex items-center gap-4 pb-2 text-fg transition-colors hover:text-accent-text"
    :class="underline ? 'border-b border-current' : 'border-b border-transparent'"
  >
    <span><slot /></span>
    <KIcon
      v-if="icon !== 'none'"
      :name="icon"
      :size="16"
      class="transition-transform duration-200 group-hover:translate-x-0.5"
      :class="icon === 'arrow-up-right' ? 'group-hover:-translate-y-0.5' : ''"
    />
  </component>
</template>
