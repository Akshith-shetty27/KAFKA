<script setup>
import { computed } from 'vue'

import KProgressBar from '@/components/ui/KProgressBar.vue'
import KStatCard from '@/components/ui/KStatCard.vue'
import { pad2, percent } from '@/utils/format'

const props = defineProps({
  summary: { type: Object, required: true },
})

const stats = computed(() => {
  const { totals, answers, streak } = props.summary
  return [
    { label: 'Completed', value: totals.completed, format: pad2, hint: `of ${totals.questions} questions` },
    { label: 'Attempted', value: totals.attempted, format: pad2, hint: 'questions opened or answered' },
    {
      label: 'MCQ accuracy',
      value: answers.accuracy,
      format: (v) => percent(v),
      decimals: 4,
      hint: answers.total ? `${answers.correct} of ${answers.total} answers correct` : 'answer an MCQ to start',
    },
    {
      label: 'Day streak',
      value: streak.current,
      format: pad2,
      hint: streak.active_today ? `best ${streak.longest} · today counted` : `best ${streak.longest} · practise today to keep it`,
      accent: true,
    },
  ]
})
</script>

<template>
  <div>
    <dl class="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
      <div v-for="stat in stats" :key="stat.label" class="border-l border-rule-soft pl-5">
        <dt class="sr-only">{{ stat.label }}</dt>
        <dd><KStatCard v-bind="stat" /></dd>
      </div>
    </dl>
    <div class="mt-10 flex items-center gap-5">
      <KProgressBar :value="summary.totals.completed" :max="summary.totals.questions" label="Overall preparation progress" />
      <span class="k-eyebrow shrink-0 text-muted">{{ percent(summary.totals.completion_rate, 1) }} overall</span>
    </div>
  </div>
</template>
