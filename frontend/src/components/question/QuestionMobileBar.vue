<script setup>
/**
 * Phones and tablets: the side rail sits far below the question, so the two
 * actions you need while reading — finishing the question and asking for
 * help — stay pinned to the bottom of the screen.
 */
import { computed } from 'vue'

import KIcon from '@/components/ui/KIcon.vue'

const props = defineProps({
  question: { type: Object, required: true },
  progress: { type: Object, default: null },
  busy: { type: Boolean, default: false },
})
const emit = defineEmits(['complete', 'ask'])

const status = computed(() => props.progress?.status ?? null)
const canComplete = computed(() => props.question.question_type !== 'mcq' && status.value !== 'completed')
const statusLabel = computed(() => {
  if (status.value === 'completed') return 'Completed'
  if (props.question.question_type === 'mcq') return props.progress?.answer_count ? 'Not yet correct' : 'Not answered'
  return status.value ? 'In progress' : 'Not started'
})
</script>

<template>
  <div
    data-surface="ink"
    class="fixed inset-x-0 bottom-0 z-30 border-t border-rule px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] lg:hidden"
  >
    <div class="mx-auto flex max-w-3xl items-center gap-3">
      <span class="flex min-w-0 flex-1 items-center gap-2.5 text-sm">
        <span
          class="size-3 shrink-0"
          :class="status === 'completed' ? 'bg-accent' : status ? 'border-[1.5px] border-accent' : 'border-[1.5px] border-rule'"
          aria-hidden="true"
        />
        <span class="truncate">{{ statusLabel }}</span>
      </span>
      <button
        type="button"
        class="k-label flex h-11 items-center gap-2 border border-rule px-3.5 text-xs hover:border-accent"
        @click="emit('ask')"
      >
        Ask Kafka
      </button>
      <button
        v-if="canComplete"
        type="button"
        class="k-label flex h-11 items-center gap-2 bg-accent px-3.5 text-xs text-on-accent disabled:opacity-50"
        :disabled="busy"
        @click="emit('complete')"
      >
        <KIcon name="check" :size="15" /> Done
      </button>
    </div>
  </div>
</template>
