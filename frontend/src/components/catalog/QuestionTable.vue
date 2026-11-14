<script setup>
import KDifficulty from '@/components/ui/KDifficulty.vue'

defineProps({
  questions: { type: Array, required: true },
  showTopic: { type: Boolean, default: true },
  showPatterns: { type: Boolean, default: false },
  showType: { type: Boolean, default: false },
})

const TYPE_LABEL = { coding: 'Code', mcq: 'MCQ', concept: 'Concept' }
const STATUS_LABEL = { completed: 'Completed', attempted: 'Attempted' }
</script>

<template>
  <ul class="border-t border-rule">
    <li v-for="q in questions" :key="q.slug" class="border-b border-rule-soft">
      <RouterLink
        :to="{ name: 'question', params: { slug: q.slug } }"
        class="group grid grid-cols-[1.25rem_minmax(0,1fr)_auto] items-center gap-x-4 gap-y-1 py-4 transition-colors hover:bg-surface sm:grid-cols-[1.25rem_minmax(0,1fr)_7rem_6.5rem] sm:px-2"
      >
        <span
          class="size-3.5"
          :class="{
            'bg-accent': q.status === 'completed',
            'border-[1.5px] border-accent bg-[linear-gradient(135deg,var(--k-accent)_50%,transparent_50%)]': q.status === 'attempted',
            'border-[1.5px] border-rule': !q.status,
          }"
          role="img"
          :aria-label="STATUS_LABEL[q.status] ?? 'Not started'"
        />
        <span class="min-w-0">
          <span class="block truncate font-medium group-hover:text-accent-text">{{ q.title }}</span>
          <span class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
            <span v-if="showTopic">{{ q.topic.name }}</span>
            <template v-if="showPatterns">
              <span v-for="p in q.patterns" :key="p.slug" class="font-mono text-xs">#{{ p.slug }}</span>
            </template>
          </span>
        </span>
        <span v-if="showType" class="k-eyebrow hidden text-muted sm:block">{{ TYPE_LABEL[q.question_type] }}</span>
        <span v-else class="hidden sm:block" />
        <KDifficulty :level="q.difficulty" class="justify-self-end" />
      </RouterLink>
    </li>
  </ul>
</template>
