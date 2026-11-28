<script setup>
/**
 * Scrollable message list. Follows the stream to the bottom while new tokens
 * arrive — unless the student has scrolled up to re-read something.
 */
import { nextTick, ref, watch } from 'vue'

import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  messages: { type: Array, required: true },
  /** Re-mounts the list per conversation, so loaded history appears at once and only new messages animate. */
  conversationKey: { type: [String, Number], default: 'new' },
})

const scroller = ref(null)
let stickToBottom = true

function onScroll() {
  const el = scroller.value
  stickToBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

watch(
  () => [props.messages.length, props.messages.at(-1)?.content],
  async () => {
    // Nothing to follow yet: keep the welcome / empty state scrolled to its top.
    if (!stickToBottom || !props.messages.length) return
    await nextTick()
    scroller.value?.scrollTo({ top: scroller.value.scrollHeight })
  },
  { immediate: true },
)

watch(
  () => props.messages.length,
  (now, before) => {
    // A message the student just sent always brings the view down.
    if (now > (before ?? 0) && props.messages.at(-2)?.role === 'user') stickToBottom = true
  },
)
</script>

<template>
  <div ref="scroller" class="min-h-0 flex-1 overflow-y-auto" role="log" aria-live="polite" aria-label="Conversation" @scroll="onScroll">
    <div class="flex flex-col gap-8 px-1 py-6">
      <slot name="before" />
      <slot v-if="!messages.length" name="empty" />
      <TransitionGroup
        :key="conversationKey"
        tag="div"
        class="flex flex-col gap-8"
        enter-active-class="transition duration-400 ease-[var(--ease-out-soft)]"
        enter-from-class="translate-y-3 opacity-0"
      >
        <ChatMessage v-for="m in messages" :key="m.id" :message="m" />
      </TransitionGroup>
    </div>
  </div>
</template>
