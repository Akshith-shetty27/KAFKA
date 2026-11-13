<script setup>
import { pad2 } from '@/utils/format'

import KIcon from './KIcon.vue'

defineProps({
  days: { type: Number, required: true },
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <div
    class="inline-flex items-center bg-accent text-on-accent"
    :class="compact ? 'gap-2.5 px-3 py-1.5' : 'gap-3 px-4 py-3.5'"
    :aria-label="`${days} day streak`"
    role="img"
  >
    <span class="k-eyebrow" :class="compact ? 'hidden sm:inline' : 'text-[11px] tracking-[0.25em]'">Daily streak</span>
    <span class="k-serif leading-none" :class="compact ? 'text-2xl' : 'text-[2.5rem]'">{{ pad2(days) }}</span>
    <KIcon name="flame" :size="compact ? 16 : 22" />
  </div>
</template>
