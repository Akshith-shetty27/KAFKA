<script setup>
import KCopyButton from '@/components/ui/KCopyButton.vue'
import KMarkdown from '@/components/ui/KMarkdown.vue'

import KAssistantMark from './KAssistantMark.vue'

defineProps({
  message: { type: Object, required: true },
})

const MODE_LABEL = { hint: 'Hint', explain: 'Explain the solution', review: 'Review my answer' }
const STATUS_NOTE = {
  incomplete: 'Stopped before the end',
  error: 'Interrupted by an error',
  refused: 'Declined',
}
</script>

<template>
  <!-- Student -->
  <div v-if="message.role === 'user'" class="flex flex-col items-end gap-1.5">
    <span v-if="message.mode !== 'chat'" class="k-eyebrow text-[10px] text-accent-text">
      {{ MODE_LABEL[message.mode] }}<template v-if="message.mode === 'hint'"> · level {{ message.hint_level }}</template>
    </span>
    <p class="max-w-[85%] bg-surface px-4 py-3 text-[15px] leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
  </div>

  <!-- KAFKA -->
  <div v-else class="border-l-2 border-accent pl-4 sm:pl-5">
    <p class="mb-3 flex items-center gap-2.5">
      <KAssistantMark :active="message.status === 'streaming'" :size="14" />
      <span class="k-eyebrow text-[10px] text-accent-text">Kafka</span>
    </p>
    <p v-if="message.status === 'streaming' && !message.content" class="k-eyebrow py-1 text-[10px] text-muted" role="status">
      Thinking…
    </p>
    <KMarkdown v-else :source="message.content" />
    <span v-if="message.status === 'streaming' && message.content" class="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-accent align-middle" aria-hidden="true" />
    <p v-if="STATUS_NOTE[message.status]" class="k-eyebrow mt-3 text-[10px] text-muted">{{ STATUS_NOTE[message.status] }}</p>
    <div v-if="message.status !== 'streaming' && message.content" class="mt-3 flex">
      <KCopyButton :text="message.content" label="Copy reply" variant="inline" />
    </div>
  </div>
</template>
