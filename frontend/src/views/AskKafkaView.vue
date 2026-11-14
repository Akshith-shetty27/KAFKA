<script setup>
/**
 * ASK KAFKA — full-page chat. /ask starts a new general conversation;
 * /ask/:id continues one (including conversations started from a question,
 * which keep their question-aware quick actions).
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ChatComposer from '@/components/assistant/ChatComposer.vue'
import ChatThread from '@/components/assistant/ChatThread.vue'
import DemoModeNote from '@/components/assistant/DemoModeNote.vue'
import QuickActions from '@/components/assistant/QuickActions.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KIcon from '@/components/ui/KIcon.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useChat } from '@/composables/useChat'
import { assistantApi } from '@/services/assistant.api'
import { useAssistantStore } from '@/stores/assistant'
import { timeAgo } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const store = useAssistantStore()

const routeId = computed(() => (route.params.id ? Number(route.params.id) : null))
const loading = ref(false)
const loadError = ref(null)
const composer = ref(null)

const chat = useChat({
  async ensureConversation() {
    if (chat.conversation.value) return chat.conversation.value
    const created = await assistantApi.create()
    // Load it first, so the route change below sees it's already open and
    // doesn't reload it while the reply is streaming in.
    chat.load(created)
    router.replace({ name: 'ask', params: { id: created.id } })
    return created
  },
})

async function open(id) {
  if (id === null) {
    chat.stop()
    chat.load(null)
    return
  }
  if (chat.conversation.value?.id === id) return // already showing it (e.g. just created)
  chat.stop()
  loading.value = true
  loadError.value = null
  try {
    chat.load(await assistantApi.get(id))
  } catch (err) {
    loadError.value = err.apiError ?? { status: 0, message: 'Could not load this conversation.' }
  } finally {
    loading.value = false
  }
}
watch(routeId, open, { immediate: true })
onMounted(store.loadConversations)

const question = computed(() => chat.conversation.value?.question ?? null)
const capabilities = computed(() => chat.conversation.value?.capabilities ?? { hint: false, explain: false, review: false })

async function deleteConversation(c) {
  if (!window.confirm(`Delete “${c.title || 'Untitled conversation'}”? This can't be undone.`)) return
  await store.remove(c.id)
  if (routeId.value === c.id) router.push({ name: 'ask' })
}

const suggestions = [
  'When should I use a sliding window instead of two pointers?',
  'Give me 3 medium dynamic programming practice problems.',
  'Explain database normalisation with a simple example.',
  'How do I solve time-and-work problems faster?',
]
function useSuggestion(text) {
  chat.send({ content: text })
}
</script>

<template>
  <div class="k-container grid grid-cols-1 gap-10 py-10 lg:grid-cols-12 lg:py-12">
    <!-- Conversation list -->
    <aside class="lg:col-span-3" :class="routeId ? 'hidden lg:block' : ''" aria-label="Conversations">
      <RouterLink
        :to="{ name: 'ask' }"
        class="k-label flex h-11 items-center justify-center gap-2 bg-accent text-xs text-on-accent hover:brightness-95"
      >
        <span aria-hidden="true">+</span> New conversation
      </RouterLink>
      <KErrorState v-if="store.listError" class="mt-6" :message="store.listError.message" @retry="store.loadConversations" />
      <KSkeleton v-else-if="store.loadingList && !store.conversations.length" class="mt-6" :lines="5" />
      <p v-else-if="!store.conversations.length" class="mt-6 text-sm text-muted">Your conversations will appear here.</p>
      <ul v-else class="mt-6 flex flex-col">
        <li v-for="c in store.conversations" :key="c.id" class="group relative border-b border-rule-soft">
          <RouterLink
            :to="{ name: 'ask', params: { id: c.id } }"
            class="block py-3.5 pr-8 transition-colors"
            :class="routeId === c.id ? 'text-fg' : 'text-muted hover:text-fg'"
            :aria-current="routeId === c.id ? 'page' : undefined"
          >
            <span class="flex items-center gap-2">
              <span v-if="routeId === c.id" class="size-1.5 shrink-0 bg-accent" aria-hidden="true" />
              <span class="truncate text-sm font-medium">{{ c.title || 'Untitled conversation' }}</span>
            </span>
            <span class="mt-1 block truncate text-xs">
              <template v-if="c.question">{{ c.question.category.name }} · </template>{{ timeAgo(c.updated_at) }}
            </span>
          </RouterLink>
          <button
            type="button"
            class="absolute top-3.5 right-0 flex size-6 items-center justify-center text-muted opacity-0 group-hover:opacity-100 hover:text-danger focus:opacity-100"
            :aria-label="`Delete ${c.title || 'conversation'}`"
            @click="deleteConversation(c)"
          >
            <KIcon name="x" :size="14" />
          </button>
        </li>
      </ul>
    </aside>

    <!-- Chat -->
    <section class="flex h-[calc(100dvh-12rem)] min-h-[32rem] flex-col lg:col-span-9" aria-label="Chat">
      <header class="flex flex-wrap items-end justify-between gap-4 border-b border-rule pb-5">
        <div class="min-w-0">
          <RouterLink v-if="routeId" :to="{ name: 'ask' }" class="k-eyebrow mb-3 inline-flex items-center gap-2 text-muted hover:text-fg lg:hidden">
            <KIcon name="arrow-left" :size="12" /> Conversations
          </RouterLink>
          <KEyebrow tone="muted">Ask Kafka<template v-if="question"> / {{ question.category.name }}</template></KEyebrow>
          <h1 class="k-display mt-3 truncate text-3xl tracking-[-0.04em] normal-case sm:text-4xl">
            {{ chat.conversation.value?.title || 'New conversation' }}
          </h1>
        </div>
        <RouterLink
          v-if="question"
          :to="{ name: 'question', params: { slug: question.slug } }"
          class="k-label inline-flex items-center gap-2 border-b border-current pb-1 text-xs hover:text-accent-text"
        >
          Open question <KIcon name="arrow-up-right" :size="14" />
        </RouterLink>
      </header>

      <KEmptyState v-if="loadError?.status === 404" class="mt-8" title="Conversation not found">
        It may have been deleted. <RouterLink :to="{ name: 'ask' }" class="underline underline-offset-4">Start a new one</RouterLink>.
      </KEmptyState>
      <KErrorState v-else-if="loadError" class="mt-8" :message="loadError.message" @retry="open(routeId)" />
      <div v-else-if="loading" class="mt-8"><KSkeleton :lines="6" height="1.25rem" /></div>

      <template v-else>
        <ChatThread :messages="chat.messages.value">
          <template #empty>
            <div class="flex flex-col gap-8 pt-8">
              <div>
                <p class="k-display text-5xl sm:text-6xl">
                  Hints,<br />not <span class="k-serif text-[1.05em]">spoilers.</span>
                </p>
                <p class="mt-5 max-w-lg text-muted">
                  Ask about concepts, approaches, aptitude shortcuts or interview strategy. For help on a specific
                  problem, open it and use the ASK KAFKA button — KAFKA will know exactly which question you're on.
                </p>
              </div>
              <ul class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <li v-for="s in suggestions" :key="s">
                  <button
                    type="button"
                    class="h-full w-full bg-surface p-4 text-left text-sm transition-colors hover:bg-raised hover:text-accent-text disabled:opacity-50"
                    :disabled="chat.streaming.value"
                    @click="useSuggestion(s)"
                  >
                    {{ s }}
                  </button>
                </li>
              </ul>
            </div>
          </template>
        </ChatThread>

        <div class="flex flex-col gap-3 pt-4">
          <DemoModeNote />
          <KErrorState v-if="chat.error.value" :message="chat.error.value.message" :retryable="chat.error.value.retryable" @retry="chat.retry" />
          <QuickActions
            v-if="question"
            :capabilities="capabilities"
            :hints-used="chat.hintsUsed.value"
            :disabled="chat.streaming.value"
            @action="(a) => chat.send({ content: a.content, mode: a.mode, hintLevel: a.hintLevel })"
          />
          <ChatComposer ref="composer" :streaming="chat.streaming.value" @send="(content) => chat.send({ content })" @stop="chat.stop" />
        </div>
      </template>
    </section>
  </div>
</template>
