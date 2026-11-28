<script setup>
/**
 * Shown above a conversation that is about a specific question: what KAFKA is
 * looking at (title, topic, difficulty) and where the student stands on it.
 * Details come from GET /questions/{slug}/ — read-only, it records nothing.
 */
import { watch } from 'vue'

import KDifficulty from '@/components/ui/KDifficulty.vue'
import KIcon from '@/components/ui/KIcon.vue'
import { useAsync } from '@/composables/useAsync'
import { catalogApi } from '@/services/catalog.api'

const props = defineProps({
  question: { type: Object, required: true }, // { slug, title, question_type, category }
})

const detail = useAsync((slug) => catalogApi.question(slug))
watch(() => props.question.slug, (slug) => detail.run(slug), { immediate: true })

const TYPE = { coding: 'Coding problem', mcq: 'Multiple choice', concept: 'Concept question' }
const STATUS = { completed: 'Completed', attempted: 'In progress' }
</script>

<template>
  <RouterLink
    :to="{ name: 'question', params: { slug: question.slug } }"
    class="k-lift group flex items-center gap-4 border border-rule-soft bg-surface px-4 py-3 hover:border-rule"
  >
    <span class="min-w-0 flex-1">
      <span class="k-eyebrow block text-[10px] text-muted">Asking about · {{ TYPE[question.question_type] ?? 'Question' }}</span>
      <span class="mt-1 block truncate font-medium group-hover:text-accent-text">{{ question.title }}</span>
      <span class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted">
        <span>{{ question.category.name }}<template v-if="detail.data.value"> · {{ detail.data.value.topic.name }}</template></span>
        <KDifficulty v-if="detail.data.value" :level="detail.data.value.difficulty" />
        <span v-if="detail.data.value?.progress?.status" class="inline-flex items-center gap-2">
          <span class="size-2" :class="detail.data.value.progress.status === 'completed' ? 'bg-accent' : 'border border-accent'" aria-hidden="true" />
          {{ STATUS[detail.data.value.progress.status] }}
        </span>
      </span>
    </span>
    <span class="k-label hidden shrink-0 items-center gap-2 text-xs sm:inline-flex">Open <KIcon name="arrow-up-right" :size="14" /></span>
  </RouterLink>
</template>
