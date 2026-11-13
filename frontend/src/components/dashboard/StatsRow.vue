<script setup>
import { computed } from 'vue'

import KProgressBar from '@/components/ui/KProgressBar.vue'
import KStat from '@/components/ui/KStat.vue'
import { pad2, percent } from '@/utils/format'

const props = defineProps({
  summary: { type: Object, required: true },
})

const stats = computed(() => {
  const { totals, answers, streak } = props.summary
  return [
    { label: 'Completed', value: pad2(totals.completed), hint: `of ${totals.questions} questions` },
    { label: 'Attempted', value: pad2(totals.attempted), hint: 'questions opened or answered' },
    {
      label: 'MCQ accuracy',
      value: answers.accuracy === null ? '—' : percent(answers.accuracy),
      hint: answers.total ? `${answers.correct} of ${answers.total} answers correct` : 'answer an MCQ to start',
    },
    {
      label: 'Day streak',
      value: pad2(streak.current),
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
        <dd><KStat :value="stat.value" :label="stat.label" :hint="stat.hint" :accent="stat.accent" /></dd>
      </div>
    </dl>
    <div class="mt-10 flex items-center gap-5">
      <KProgressBar :value="summary.totals.completed" :max="summary.totals.questions" label="Overall preparation progress" />
      <span class="k-eyebrow shrink-0 text-muted">{{ percent(summary.totals.completion_rate, 1) }} overall</span>
    </div>
  </div>
</template>
