<script setup>
/**
 * One question. Layout adapts to the type:
 *   coding  → statement, examples, constraints, approach (reveal), solution (reveal)
 *   mcq     → statement, options, server-graded result + explanation
 *   concept → statement, model answer (reveal), SQL solution if any
 * Opening the page records an "attempt" for progress tracking.
 */
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import AssistantDrawer from '@/components/assistant/AssistantDrawer.vue'
import ExampleList from '@/components/question/ExampleList.vue'
import McqOptions from '@/components/question/McqOptions.vue'
import QuestionAside from '@/components/question/QuestionAside.vue'
import RevealPanel from '@/components/question/RevealPanel.vue'
import KCodeBlock from '@/components/ui/KCodeBlock.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KMarkdown from '@/components/ui/KMarkdown.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useAsync } from '@/composables/useAsync'
import { catalogApi } from '@/services/catalog.api'
import { progressApi } from '@/services/progress.api'
import { toApiError } from '@/services/http'

const route = useRoute()
const slug = computed(() => route.params.slug)

const detail = useAsync((s) => catalogApi.question(s))
const question = computed(() => detail.data.value)
const progress = ref(null)
const reveal = reactive({ approach: false, solution: false })

// MCQ result once graded: { selectedId, correctId, explanation, isCorrect }
const mcqResult = ref(null)

async function load(s) {
  reveal.approach = false
  reveal.solution = false
  mcqResult.value = null
  progress.value = null
  const data = await detail.run(s)
  if (!data) return
  progress.value = data.progress
  if (data.question_type === 'mcq' && data.answer && data.progress?.selected_option_id) {
    mcqResult.value = {
      selectedId: data.progress.selected_option_id,
      correctId: data.answer.correct_option_id,
      explanation: data.explanation,
      isCorrect: data.progress.is_correct,
    }
  }
  document.title = `${data.title} · KAFKA`
  // Record the visit; failures here shouldn't disturb reading.
  progressApi
    .attempt(s)
    .then((p) => {
      if (slug.value === s) progress.value = p
    })
    .catch(() => {})
}
watch(slug, load, { immediate: true })

// --- actions ---------------------------------------------------------------------------
const busy = ref(false)
const actionError = ref(null)

async function act(fn) {
  busy.value = true
  actionError.value = null
  try {
    await fn()
  } catch (err) {
    actionError.value = err.apiError ?? toApiError(err)
  } finally {
    busy.value = false
  }
}

const submitAnswer = (optionId) =>
  act(async () => {
    const r = await progressApi.answer(slug.value, optionId)
    progress.value = r.progress
    mcqResult.value = { selectedId: optionId, correctId: r.correct_option_id, explanation: r.explanation, isCorrect: r.is_correct }
  })

const markComplete = () =>
  act(async () => {
    progress.value = await progressApi.complete(slug.value)
  })

const resetProgress = () =>
  act(async () => {
    await progressApi.reset(slug.value)
    progress.value = null
    mcqResult.value = null
  })

// Already ordered by the API with my preferred language first.
const solutions = computed(() => question.value?.solutions ?? [])

// --- ASK KAFKA -------------------------------------------------------------------------
// Mirrors the server's rules (apps/assistant/context.py); the server re-checks.
const askOpen = ref(false)
const askCapabilities = computed(() => {
  if (!question.value) return { hint: false, explain: false, review: false }
  const answered = Boolean(progress.value?.answer_count)
  if (question.value.question_type === 'mcq') return { hint: !answered, explain: answered, review: answered }
  return { hint: true, explain: true, review: false }
})
watch(slug, () => (askOpen.value = false))
</script>

<template>
  <div class="k-container py-10 lg:py-14">
    <KErrorState
      v-if="detail.error.value && detail.error.value.status !== 404"
      :message="detail.error.value.message"
      @retry="load(slug)"
    />
    <KEmptyState v-else-if="detail.error.value" title="Question not found">
      It may have been moved or unpublished.
      <RouterLink :to="{ name: 'prepare' }" class="underline underline-offset-4">Browse topics</RouterLink>.
    </KEmptyState>

    <div v-else-if="!question" class="grid grid-cols-1 gap-12 lg:grid-cols-12">
      <div class="lg:col-span-8"><KSkeleton :lines="10" height="1.25rem" /></div>
    </div>

    <template v-else>
      <!-- Breadcrumb -->
      <nav class="k-eyebrow flex flex-wrap items-center gap-x-3 gap-y-2 text-muted" aria-label="Breadcrumb">
        <RouterLink :to="{ name: 'practice', params: { category: question.category.slug } }" class="hover:text-fg">
          {{ question.category.name }}
        </RouterLink>
        <span aria-hidden="true">/</span>
        <RouterLink
          :to="{ name: 'practice', params: { category: question.category.slug }, query: { topic: question.topic.slug } }"
          class="hover:text-fg"
        >
          {{ question.topic.name }}
        </RouterLink>
      </nav>

      <div class="mt-8 grid grid-cols-1 gap-14 lg:grid-cols-12 lg:gap-12">
        <article class="min-w-0 lg:col-span-8">
          <h1 class="k-display text-[clamp(2.25rem,5vw,3.75rem)] leading-[0.95] normal-case tracking-[-0.035em]">
            {{ question.title }}
          </h1>

          <!-- Statement -->
          <section class="mt-10">
            <KMarkdown :source="question.statement" size="lg" />
          </section>

          <!-- ============================== CODING ============================== -->
          <template v-if="question.question_type === 'coding' && question.coding">
            <section v-if="question.coding.examples.length" class="mt-10">
              <KEyebrow as="h2" class="mb-5">Examples</KEyebrow>
              <ExampleList :examples="question.coding.examples" />
            </section>

            <section v-if="question.coding.constraints" class="mt-10">
              <KEyebrow as="h2" class="mb-4">Constraints</KEyebrow>
              <KMarkdown :source="question.coding.constraints" />
            </section>

            <div class="mt-14 flex flex-col gap-10">
              <RevealPanel
                v-model:open="reveal.approach"
                index="01"
                title="Approach"
                prompt="Give it a real try first. Open the approach when you're stuck — it explains the idea, not the code."
                action-label="Show approach"
              >
                <KMarkdown :source="question.coding.approach" />
              </RevealPanel>

              <RevealPanel
                v-model:open="reveal.solution"
                index="02"
                title="Solution"
                prompt="Full code and the reasoning behind it."
                action-label="Show solution"
              >
                <KCodeBlock v-if="solutions.length" :solutions="solutions" />
                <div class="mt-8">
                  <KEyebrow as="h3" tone="muted" class="mb-4">Why it works</KEyebrow>
                  <KMarkdown :source="question.explanation" />
                </div>
              </RevealPanel>
            </div>
          </template>

          <!-- =============================== MCQ =============================== -->
          <template v-else-if="question.question_type === 'mcq'">
            <section class="mt-10">
              <McqOptions
                :options="question.options"
                :result="mcqResult"
                :submitting="busy"
                @submit="submitAnswer"
              />
            </section>

            <section v-if="mcqResult" class="mt-10 border-t border-rule pt-8" aria-live="polite">
              <p class="k-display text-4xl normal-case tracking-[-0.03em]" :class="mcqResult.isCorrect ? 'text-accent-text' : 'text-danger'">
                {{ mcqResult.isCorrect ? 'Correct.' : 'Not quite.' }}
              </p>
              <div class="mt-6">
                <KEyebrow as="h2" tone="muted" class="mb-4">Explanation</KEyebrow>
                <KMarkdown :source="mcqResult.explanation" />
              </div>
              <div class="mt-10 flex flex-wrap items-center gap-x-10 gap-y-4">
                <button
                  v-if="!mcqResult.isCorrect"
                  type="button"
                  class="k-label inline-flex items-center gap-3 border-b border-current pb-2 text-accent-text"
                  @click="askOpen = true"
                >
                  Ask Kafka why →
                </button>
                <RouterLink
                  v-if="question.navigation.next"
                  :to="{ name: 'question', params: { slug: question.navigation.next } }"
                  class="k-label inline-flex items-center gap-3 border-b border-current pb-2 hover:text-accent-text"
                >
                  Next question →
                </RouterLink>
              </div>
            </section>
          </template>

          <!-- ============================= CONCEPT ============================= -->
          <template v-else>
            <div class="mt-14">
              <RevealPanel
                v-model:open="reveal.solution"
                index="01"
                title="Model answer"
                prompt="Say your answer out loud (or write it down) first — that's what the interview will ask of you."
                action-label="Reveal answer"
              >
                <KMarkdown :source="question.explanation" />
                <div v-if="solutions.length" class="mt-8">
                  <KEyebrow as="h3" tone="muted" class="mb-4">Query</KEyebrow>
                  <KCodeBlock :solutions="solutions" />
                </div>
              </RevealPanel>
            </div>
          </template>
        </article>

        <aside class="lg:col-span-4">
          <div class="lg:sticky lg:top-28">
            <QuestionAside
              :question="question"
              :progress="progress"
              :busy="busy"
              :error="actionError"
              @complete="markComplete"
              @reset="resetProgress"
              @ask="askOpen = true"
            />
          </div>
        </aside>
      </div>

      <AssistantDrawer v-model:open="askOpen" :question="question" :capabilities="askCapabilities" />
    </template>
  </div>
</template>
