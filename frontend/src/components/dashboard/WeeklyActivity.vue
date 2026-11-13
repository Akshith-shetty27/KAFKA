<script setup>
import { computed } from 'vue'

import KBarChart from '@/components/ui/KBarChart.vue'
import { longDate, weekdayInitial } from '@/utils/format'

const props = defineProps({
  series: { type: Array, required: true }, // [{ date, questions, completed, answered, ai_messages }]
})

const bars = computed(() =>
  props.series.map((day) => ({ label: weekdayInitial(day.date), value: day.questions, title: longDate(day.date) })),
)
const totals = computed(() =>
  props.series.reduce(
    (acc, d) => ({ questions: acc.questions + d.questions, completed: acc.completed + d.completed, answered: acc.answered + d.answered }),
    { questions: 0, completed: 0, answered: 0 },
  ),
)
const activeDays = computed(() => props.series.filter((d) => d.questions > 0).length)
</script>

<template>
  <div>
    <KBarChart :data="bars" label="Questions practised per day, last 7 days" :height="148" highlight-last />
    <dl class="mt-8 grid grid-cols-3 gap-4 border-t border-rule-soft pt-6">
      <div>
        <dt class="k-eyebrow text-muted">Questions</dt>
        <dd class="k-serif mt-2 text-4xl">{{ totals.questions }}</dd>
      </div>
      <div>
        <dt class="k-eyebrow text-muted">Completed</dt>
        <dd class="k-serif mt-2 text-4xl">{{ totals.completed }}</dd>
      </div>
      <div>
        <dt class="k-eyebrow text-muted">Active days</dt>
        <dd class="k-serif mt-2 text-4xl">{{ activeDays }}<span class="text-xl text-muted">/7</span></dd>
      </div>
    </dl>
  </div>
</template>
