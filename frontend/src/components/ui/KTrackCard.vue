<script setup>
/**
 * A preparation track as one interactive card: glyph, name, what it covers,
 * and the student's real progress as a ring. The whole card is a link, so it
 * works the same with a mouse, touch or the keyboard (lift on hover *and* focus).
 */
import { computed } from 'vue'

import { percent } from '@/utils/format'

import KIcon from './KIcon.vue'
import KProgressRing from './KProgressRing.vue'

const props = defineProps({
  to: { type: [String, Object], required: true },
  index: { type: Number, required: true },
  glyph: { type: String, default: '' },
  name: { type: String, required: true },
  description: { type: String, default: '' },
  completed: { type: Number, required: true },
  total: { type: Number, required: true },
  attempted: { type: Number, default: 0 },
  /** Smaller card without the description (dashboard grid). */
  compact: { type: Boolean, default: false },
})

const share = computed(() => (props.total ? props.completed / props.total : 0))
</script>

<template>
  <RouterLink
    :to="to"
    class="k-lift group flex h-full flex-col border border-rule-soft bg-surface outline-offset-4 hover:border-rule"
    :class="compact ? 'p-5' : 'p-6 sm:p-7'"
  >
    <div class="flex items-start justify-between gap-4">
      <span class="font-mono text-sm text-muted">{{ String(index).padStart(2, '0') }}</span>
      <KProgressRing :value="completed" :max="total" :label="`${name} progress`" :size="compact ? 52 : 64">
        <span class="font-mono text-xs">{{ percent(share) }}</span>
      </KProgressRing>
    </div>
    <p
      class="k-serif leading-none not-italic transition-colors group-hover:text-accent-text"
      :class="compact ? 'my-4 text-5xl' : 'my-6 text-[5rem]'"
      aria-hidden="true"
    >
      {{ glyph }}
    </p>
    <component :is="compact ? 'h3' : 'h2'" class="font-medium tracking-tight uppercase" :class="compact ? 'flex-1 text-lg leading-tight' : 'text-2xl'">
      {{ name }}
    </component>
    <p v-if="!compact" class="mt-3 flex-1 text-muted">{{ description }}</p>
    <div class="mt-6 flex items-end justify-between gap-4 border-t border-rule-soft pt-4">
      <p class="text-sm text-muted">
        <span class="font-mono text-fg">{{ completed }}/{{ total }}</span> done · {{ attempted }} attempted
      </p>
      <span class="k-label inline-flex items-center gap-2 text-xs transition-transform group-hover:translate-x-0.5">
        <span :class="compact ? 'sr-only' : ''">Practice</span> <KIcon name="arrow-up-right" :size="14" />
      </span>
    </div>
  </RouterLink>
</template>
