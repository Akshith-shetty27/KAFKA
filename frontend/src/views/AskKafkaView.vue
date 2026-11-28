<script setup>
/**
 * ASK KAFKA — full-page chat. /ask starts a new general conversation;
 * /ask/:id continues one (including conversations started from a question,
 * which keep their question-aware quick actions). The sidebar also holds the
 * student's study plans (generated from a pasted job description).
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ChatComposer from '@/components/assistant/ChatComposer.vue'
import ChatThread from '@/components/assistant/ChatThread.vue'
import DemoModeNote from '@/components/assistant/DemoModeNote.vue'
import KAssistantMark from '@/components/assistant/KAssistantMark.vue'
import QuestionContextCard from '@/components/assistant/QuestionContextCard.vue'
import QuickActions from '@/components/assistant/QuickActions.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KIcon from '@/components/ui/KIcon.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useChat } from '@/composables/useChat'
import { assistantApi } from '@/services/assistant.api'
import { useToast } from '@/composables/useToast'
import { prepApi } from '@/services/prep.api'
import { progressApi } from '@/services/progress.api'
import { useAssistantStore } from '@/stores/assistant'
import { timeAgo } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const store = useAssistantStore()
const toast = useToast()

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

// Study plans (newest first). A failure here only hides the list — chat still works.
const plans = ref([])
const plansError = ref(false)
onMounted(async () => {
  try {
    plans.value = (await prepApi.list({ page_size: 5 })).results
  } catch {
    plansError.value = true
  }
})

const question = computed(() => chat.conversation.value?.question ?? null)
const capabilities = computed(() => chat.conversation.value?.capabilities ?? { hint: false, explain: false, review: false })

async function deleteConversation(c) {
  if (!window.confirm(`Delete “${c.title || 'Untitled conversation'}”? This can't be undone.`)) return
  try {
    await store.remove(c.id)
  } catch (err) {
    toast.error(`Couldn't delete the conversation: ${err.apiError?.message ?? 'please try again.'}`)
    return
  }
  toast.success('Conversation deleted.')
  if (routeId.value === c.id) router.push({ name: 'ask' })
}

// Suggestions: two built from the student's own recommended topics (real progress
// data), topped up with general ones. Tags say what kind of help each is.
const GENERAL = [
  { tag: 'Compare', text: 'When should I use a sliding window instead of two pointers?' },
  { tag: 'Practice', text: 'Give me 3 medium dynamic programming practice problems.' },
  { tag: 'Explain', text: 'Explain database normalisation with a simple example.' },
  { tag: 'Shortcut', text: 'How do I solve time-and-work problems faster?' },
]
const recommended = ref([])
onMounted(async () => {
  try {
    recommended.value = (await progressApi.plan()).recommended_topics.slice(0, 2)
  } catch {
    recommended.value = [] // suggestions still work without personal ones
  }
})
const suggestions = computed(() => {
  const personal = recommended.value.map((t, i) =>
    i === 0
      ? { tag: 'Your next topic', text: `Teach me ${t.name} from the basics, with one worked example.` }
      : { tag: 'Your next topic', text: `Quiz me with 3 quick questions on ${t.name}.` },
  )
  return [...personal, ...GENERAL].slice(0, 4)
})
function useSuggestion(text) {
  chat.send({ content: text })
}
</script>

<template>
  <div class="k-container grid grid-cols-1 gap-10 py-10 lg:grid-cols-12 lg:py-12">
    <!-- Conversation list -->
    <aside class="lg:col-span-3" :class="routeId ? 'hidden lg:block' : ''" aria-label="Conversations">
      <RouterLink
        :to="{ name: 'plan-new' }"
        class="k-label flex h-11 items-center justify-center gap-2 border border-rule text-xs hover:border-accent hover:text-accent-text"
      >
        <span aria-hidden="true">+</span> New study plan
      </RouterLink>

      <section v-if="plans.length" class="mt-8" aria-labelledby="plans-title">
        <p id="plans-title" class="k-eyebrow text-muted">Study plans</p>
        <ul class="mt-3 flex flex-col">
          <li v-for="p in plans" :key="p.id" class="border-b border-rule-soft">
            <RouterLink :to="{ name: 'plan', params: { id: p.id } }" class="block py-3 text-muted transition-colors hover:text-fg">
              <span class="block truncate text-sm font-medium">{{ p.role }}<template v-if="p.company"> · {{ p.company }}</template></span>
              <span class="mt-1 flex items-center gap-3 text-xs">
                <span class="font-mono">{{ p.progress.completed_items }}/{{ p.progress.total_items }}</span>
                <span class="h-[3px] flex-1 bg-rule-soft">
                  <span
                    class="block h-full bg-accent"
                    :style="{ width: `${p.progress.total_items ? (100 * p.progress.completed_items) / p.progress.total_items : 0}%` }"
                  />
                </span>
              </span>
            </RouterLink>
          </li>
        </ul>
      </section>
      <p v-if="plans.length || store.conversations.length" class="k-eyebrow mt-8 text-muted">Conversations</p>
      <KErrorState v-if="store.listError" class="mt-3" :message="store.listError.message" @retry="store.loadConversations" />
      <KSkeleton v-else-if="store.loadingList && !store.conversations.length" class="mt-3" :lines="5" />
      <p v-else-if="!store.conversations.length" class="mt-3 text-sm text-muted">Your conversations will appear here.</p>
      <ul v-else class="mt-3 flex flex-col">
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
          <p class="flex items-center gap-3">
            <KAssistantMark :active="chat.streaming.value" :size="16" />
            <KEyebrow tone="muted" as="span">Ask Kafka<template v-if="question"> / {{ question.category.name }}</template></KEyebrow>
          </p>
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
        <ChatThread :messages="chat.messages.value" :conversation-key="chat.conversation.value?.id ?? 'new'">
          <template v-if="question" #before>
            <QuestionContextCard :question="question" />
          </template>
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
              <RouterLink
                :to="{ name: 'plan-new' }"
                class="group flex flex-col gap-2 border border-rule p-5 transition-colors hover:border-accent sm:flex-row sm:items-center sm:justify-between sm:gap-6"
              >
                <span>
                  <span class="block font-medium group-hover:text-accent-text">Preparing for a specific job?</span>
                  <span class="mt-1 block text-sm text-muted">Paste the job description and KAFKA builds a study plan for that exact role.</span>
                </span>
                <span class="k-label inline-flex shrink-0 items-center gap-2 text-xs">Build my plan <KIcon name="arrow-up-right" :size="14" /></span>
              </RouterLink>
              <ul class="grid grid-cols-1 gap-3 sm:grid-cols-2" aria-label="Suggested questions">
                <li v-for="(s, i) in suggestions" :key="s.text" class="k-rise" :style="{ '--i': i }">
                  <button
                    type="button"
                    class="k-lift group flex h-full w-full flex-col gap-2 border border-rule-soft bg-surface p-4 text-left hover:border-rule disabled:opacity-50"
                    :disabled="chat.streaming.value"
                    @click="useSuggestion(s.text)"
                  >
                    <span class="k-eyebrow text-[10px]" :class="s.tag === 'Your next topic' ? 'text-accent-text' : 'text-muted'">{{ s.tag }}</span>
                    <span class="text-sm leading-relaxed group-hover:text-accent-text">{{ s.text }}</span>
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
