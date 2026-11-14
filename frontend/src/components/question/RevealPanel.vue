<script setup>
/**
 * A step the student opens deliberately ("Show approach", "Show solution").
 * Hidden by default so the page nudges thinking before reading.
 */
import { useId } from 'vue'

import KIcon from '@/components/ui/KIcon.vue'

const open = defineModel('open', { type: Boolean, default: false })
defineProps({
  index: { type: String, required: true },
  title: { type: String, required: true },
  prompt: { type: String, required: true }, // e.g. "Try for 10 minutes first."
  actionLabel: { type: String, required: true },
})
const id = useId()
</script>

<template>
  <section class="border-t border-rule pt-6">
    <div class="flex flex-wrap items-baseline justify-between gap-4">
      <h2 class="k-eyebrow">{{ title }} / {{ index }}</h2>
      <button
        type="button"
        class="k-label inline-flex items-center gap-2 text-xs transition-colors hover:text-accent-text"
        :aria-expanded="open"
        :aria-controls="id"
        @click="open = !open"
      >
        {{ open ? 'Hide' : actionLabel }}
        <KIcon name="chevron-right" :size="14" class="transition-transform" :class="open ? 'rotate-90' : ''" />
      </button>
    </div>
    <p v-if="!open" class="mt-3 text-sm text-muted">{{ prompt }}</p>
    <div v-show="open" :id="id" class="mt-6">
      <slot />
    </div>
  </section>
</template>
