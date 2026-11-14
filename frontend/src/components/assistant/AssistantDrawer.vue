<script setup>
/**
 * ASK KAFKA beside a question. Opens the most recent conversation about this
 * question (or starts one on the first message). Quick actions follow the
 * same rules the server enforces, passed in as `capabilities`.
 */
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import KErrorState from '@/components/ui/KErrorState.vue'
import KIcon from '@/components/ui/KIcon.vue'
import { useChat } from '@/composables/useChat'
import { assistantApi } from '@/services/assistant.api'

import ChatComposer from './ChatComposer.vue'
import ChatThread from './ChatThread.vue'
import DemoModeNote from './DemoModeNote.vue'
import QuickActions from './QuickActions.vue'

const open = defineModel('open', { type: Boolean, default: false })
const props = defineProps({
  question: { type: Object, required: true }, // question detail
  capabilities: { type: Object, required: true },
})

const loading = ref(false)
const loadError = ref(null)
const loadedFor = ref(null)
const composer = ref(null)

const chat = useChat({
  ensureConversation: async () => chat.conversation.value ?? (await assistantApi.create(props.question.slug)),
})

async function loadForQuestion(slug) {
  loading.value = true
  loadError.value = null
  try {
    const { results } = await assistantApi.list({ question: slug, page_size: 1 })
    chat.load(results.length ? await assistantApi.get(results[0].id) : null)
    loadedFor.value = slug
  } catch (err) {
    loadError.value = err.apiError ?? { message: 'Could not load the conversation.' }
  } finally {
    loading.value = false
  }
}

watch(open, async (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : '' // keep the page behind still
  if (!isOpen) return
  if (loadedFor.value !== props.question.slug) await loadForQuestion(props.question.slug)
  await nextTick()
  composer.value?.focus()
})

// Navigating to another question resets the drawer to that question.
watch(
  () => props.question.slug,
  () => {
    chat.stop()
    loadedFor.value = null
    if (open.value) loadForQuestion(props.question.slug)
  },
)

function onKey(event) {
  if (event.key === 'Escape' && open.value) open.value = false
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
  chat.stop()
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="fixed inset-0 z-40 bg-ink-950/50 backdrop-blur-[2px]" aria-hidden="true" @click="open = false" />
    </Transition>
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      leave-active-class="transition-transform duration-200 ease-in"
      enter-from-class="translate-x-full"
      leave-to-class="translate-x-full"
    >
      <aside
        v-if="open"
        data-surface="ink"
        class="fixed inset-y-0 right-0 z-50 flex w-full max-w-xl flex-col border-l border-rule shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-label="ASK KAFKA"
      >
        <header class="flex items-start justify-between gap-6 border-b border-rule px-5 py-5 sm:px-7">
          <div class="min-w-0">
            <p class="k-display text-2xl tracking-[-0.04em]">Ask Kafka<span class="text-accent">.</span></p>
            <p class="mt-1 truncate text-sm text-muted">{{ question.title }}</p>
          </div>
          <div class="flex items-center gap-4">
            <RouterLink
              v-if="chat.conversation.value"
              :to="{ name: 'ask', params: { id: chat.conversation.value.id } }"
              class="k-eyebrow hidden text-[10px] text-muted hover:text-fg sm:block"
            >
              Open full chat
            </RouterLink>
            <button
              type="button"
              class="-mr-2 flex size-10 items-center justify-center hover:text-accent"
              aria-label="Close ASK KAFKA"
              @click="open = false"
            >
              <KIcon name="close" :size="22" />
            </button>
          </div>
        </header>

        <div class="flex min-h-0 flex-1 flex-col px-5 sm:px-7">
          <KErrorState v-if="loadError" class="mt-6" :message="loadError.message" @retry="loadForQuestion(question.slug)" />
          <div v-else-if="loading" class="flex flex-1 items-center justify-center text-sm text-muted">Loading…</div>
          <ChatThread v-else :messages="chat.messages.value">
            <template #empty>
              <div class="flex flex-col gap-4 pt-6">
                <p class="k-serif text-4xl leading-tight">Stuck? Start small.</p>
                <p class="text-sm leading-relaxed text-muted">
                  KAFKA knows the problem you're on. Hints come in three levels and never include the full solution —
                  ask for an explanation only when you're ready.
                </p>
              </div>
            </template>
          </ChatThread>
        </div>

        <footer class="flex flex-col gap-3 border-t border-rule px-5 py-4 sm:px-7">
          <DemoModeNote />
          <KErrorState
            v-if="chat.error.value"
            :message="chat.error.value.message"
            :retryable="chat.error.value.retryable"
            @retry="chat.retry"
          />
          <QuickActions
            :capabilities="capabilities"
            :hints-used="chat.hintsUsed.value"
            :disabled="chat.streaming.value || loading"
            @action="(a) => chat.send({ content: a.content, mode: a.mode, hintLevel: a.hintLevel })"
          />
          <ChatComposer
            ref="composer"
            :streaming="chat.streaming.value"
            placeholder="Ask about this question…"
            @send="(content) => chat.send({ content })"
            @stop="chat.stop"
          />
        </footer>
      </aside>
    </Transition>
  </Teleport>
</template>
