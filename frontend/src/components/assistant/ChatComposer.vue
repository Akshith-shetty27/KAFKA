<script setup>
/** Message box: Enter sends, Shift+Enter adds a line; Stop while streaming. */
import { computed, nextTick, ref, watch } from 'vue'

import KIcon from '@/components/ui/KIcon.vue'

const props = defineProps({
  streaming: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Ask KAFKA anything about your preparation…' },
})
const emit = defineEmits(['send', 'stop'])

const MAX = 4000
const text = ref('')
const box = ref(null)
const tooLong = computed(() => text.value.length > MAX)
const canSend = computed(() => !props.streaming && text.value.trim().length > 0 && !tooLong.value)

function autosize() {
  const el = box.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 200)}px`
}
watch(text, () => nextTick(autosize))

function submit() {
  if (!canSend.value) return
  emit('send', text.value.trim())
  text.value = ''
}

function onKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    submit()
  }
}

defineExpose({ focus: () => box.value?.focus() })
</script>

<template>
  <form class="border border-rule-soft bg-canvas focus-within:border-accent" @submit.prevent="submit">
    <label class="sr-only" for="kafka-composer">Message ASK KAFKA</label>
    <textarea
      id="kafka-composer"
      ref="box"
      v-model="text"
      rows="1"
      :placeholder="placeholder"
      class="block max-h-[200px] w-full resize-none bg-transparent px-4 pt-3.5 pb-1 text-[15px] leading-relaxed outline-none placeholder:text-muted/70"
      @keydown="onKeydown"
    />
    <div class="flex items-center justify-between gap-3 px-3 pb-2.5">
      <span class="text-xs text-muted" :class="tooLong ? 'text-danger' : ''">
        <template v-if="text.length > MAX - 400">{{ text.length }}/{{ MAX }}</template>
        <template v-else>Enter to send · Shift+Enter for a new line</template>
      </span>
      <button
        v-if="streaming"
        type="button"
        class="k-label inline-flex h-9 items-center gap-2 border border-rule px-3 text-xs hover:border-fg"
        @click="emit('stop')"
      >
        <span class="size-2.5 bg-current" aria-hidden="true" /> Stop
      </button>
      <button
        v-else
        type="submit"
        class="flex size-9 items-center justify-center bg-accent text-on-accent transition-opacity disabled:opacity-30"
        :disabled="!canSend"
        aria-label="Send message"
      >
        <KIcon name="arrow-up-right" :size="16" />
      </button>
    </div>
  </form>
</template>
