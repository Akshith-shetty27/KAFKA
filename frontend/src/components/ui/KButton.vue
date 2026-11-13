<script setup>
/**
 * Solid button for actions (form submits, app actions). Marketing CTAs use
 * KArrowLink instead. Variants:
 *   accent – teal fill (primary action)
 *   solid  – foreground fill (black on Paper, cream on Ink)
 *   ghost  – hairline outline
 */
import KIcon from './KIcon.vue'

defineProps({
  variant: { type: String, default: 'accent' },
  type: { type: String, default: 'button' },
  to: { type: [String, Object], default: null },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
  icon: { type: String, default: null },
})
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'button'"
    :to="to ?? undefined"
    :type="to ? undefined : type"
    :disabled="to ? undefined : disabled || loading"
    :aria-busy="loading || undefined"
    class="k-label relative inline-flex min-h-12 items-center justify-center gap-3 px-6 transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50"
    :class="[
      block ? 'w-full' : '',
      {
        'bg-accent text-on-accent hover:brightness-95': variant === 'accent',
        'bg-fg text-canvas hover:opacity-90': variant === 'solid',
        'border border-rule text-fg hover:border-fg': variant === 'ghost',
      },
    ]"
  >
    <span :class="loading ? 'invisible' : ''" class="inline-flex items-center gap-3">
      <slot />
      <KIcon v-if="icon" :name="icon" :size="16" />
    </span>
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center" aria-hidden="true">
      <span class="size-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
    </span>
  </component>
</template>
