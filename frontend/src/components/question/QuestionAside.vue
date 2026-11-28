<script setup>
/**
 * Sticky right rail on question pages: my status, the complete / reset
 * actions, question facts, and previous / next within the topic.
 */
import { computed } from 'vue'

import KButton from '@/components/ui/KButton.vue'
import KDifficulty from '@/components/ui/KDifficulty.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KIcon from '@/components/ui/KIcon.vue'

const props = defineProps({
  /** Completed by an action on this page just now (plays a short confirmation). */
  justCompleted: { type: Boolean, default: false },
  question: { type: Object, required: true },
  progress: { type: Object, default: null },
  busy: { type: Boolean, default: false },
  error: { type: Object, default: null },
})
const emit = defineEmits(['complete', 'reset', 'ask'])

const status = computed(() => props.progress?.status ?? null)
const isMcq = computed(() => props.question.question_type === 'mcq')
const completeLabel = computed(() => (props.question.question_type === 'concept' ? 'Mark as understood' : 'Mark as solved'))
</script>

<template>
  <div class="flex flex-col gap-8">
    <!-- ASK KAFKA -->
    <button
      type="button"
      data-surface="ink"
      class="group k-grid flex items-center justify-between gap-4 border border-rule p-5 text-left transition-colors hover:border-accent"
      @click="emit('ask')"
    >
      <span>
        <span class="k-display block text-xl tracking-[-0.04em]">Ask Kafka<span class="text-accent">.</span></span>
        <span class="mt-1 block text-sm text-muted">Stuck? Get a hint, not the answer.</span>
      </span>
      <KIcon name="arrow-up-right" :size="18" class="text-accent transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
    </button>

    <!-- Status + actions -->
    <div class="bg-surface p-6">
      <p class="k-eyebrow text-muted">Your status</p>
      <p class="mt-3 flex items-center gap-3 text-lg font-medium">
        <span
          class="size-3.5"
          :class="[
            status === 'completed' ? 'bg-accent' : status === 'attempted' ? 'border-[1.5px] border-accent' : 'border-[1.5px] border-rule',
            justCompleted ? 'k-status-pop' : '',
          ]"
          aria-hidden="true"
        />
        {{ status === 'completed' ? 'Completed' : status === 'attempted' ? (isMcq && progress?.answer_count ? 'Answered — not yet correct' : 'In progress') : 'Not started' }}
      </p>
      <p v-if="isMcq && progress?.answer_count" class="mt-2 text-sm text-muted">
        First attempt {{ progress.first_attempt_correct ? 'correct' : 'incorrect' }} · {{ progress.answer_count }}
        {{ progress.answer_count === 1 ? 'answer' : 'answers' }}
      </p>

      <div class="mt-6 flex flex-col gap-3">
        <KButton v-if="!isMcq && status !== 'completed'" block :loading="busy" icon="check" @click="emit('complete')">
          {{ completeLabel }}
        </KButton>
        <p v-if="isMcq && status !== 'completed'" class="text-sm text-muted">Answer correctly to complete this question.</p>
        <button
          v-if="progress"
          type="button"
          class="k-eyebrow inline-flex items-center gap-2 self-start text-muted hover:text-fg disabled:opacity-50"
          :disabled="busy"
          @click="emit('reset')"
        >
          <KIcon name="refresh" :size="13" /> {{ isMcq ? 'Reset & try again' : 'Reset progress' }}
        </button>
      </div>
      <KErrorState v-if="error" class="mt-4" :message="error.message" :retryable="false" />
    </div>

    <!-- Facts -->
    <dl class="grid grid-cols-2 gap-x-6 gap-y-5 border-t border-rule pt-6">
      <div>
        <dt class="k-eyebrow text-muted">Difficulty</dt>
        <dd class="mt-2"><KDifficulty :level="question.difficulty" /></dd>
      </div>
      <div>
        <dt class="k-eyebrow text-muted">Topic</dt>
        <dd class="mt-2 text-sm">{{ question.topic.name }}</dd>
      </div>
      <template v-if="question.coding">
        <div>
          <dt class="k-eyebrow text-muted">Time</dt>
          <dd class="mt-2 font-mono text-sm">{{ question.coding.time_complexity || '—' }}</dd>
        </div>
        <div>
          <dt class="k-eyebrow text-muted">Space</dt>
          <dd class="mt-2 font-mono text-sm">{{ question.coding.space_complexity || '—' }}</dd>
        </div>
      </template>
      <div v-if="question.patterns.length" class="col-span-2">
        <dt class="k-eyebrow text-muted">Patterns</dt>
        <dd class="mt-2 flex flex-wrap gap-2">
          <RouterLink
            v-for="p in question.patterns"
            :key="p.slug"
            :to="{ name: 'practice', params: { category: question.category.slug }, query: { pattern: p.slug } }"
            class="border border-rule-soft px-2.5 py-1 font-mono text-xs hover:border-accent hover:text-accent-text"
          >
            {{ p.name }}
          </RouterLink>
        </dd>
      </div>
    </dl>

    <!-- Prev / next -->
    <nav class="grid grid-cols-2 gap-3 border-t border-rule pt-6" aria-label="Questions in this topic">
      <RouterLink
        v-if="question.navigation.previous"
        :to="{ name: 'question', params: { slug: question.navigation.previous } }"
        class="k-label inline-flex items-center gap-2 text-xs text-muted hover:text-fg"
      >
        <KIcon name="arrow-left" :size="14" /> Previous
      </RouterLink>
      <span v-else />
      <RouterLink
        v-if="question.navigation.next"
        :to="{ name: 'question', params: { slug: question.navigation.next } }"
        class="k-label inline-flex items-center justify-end gap-2 text-xs hover:text-accent-text"
      >
        Next <KIcon name="arrow-right" :size="14" />
      </RouterLink>
    </nav>
  </div>
</template>
