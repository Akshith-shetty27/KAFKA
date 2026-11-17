<script setup>
/**
 * Activity over the last 90 days (/progress/activity?days=90): an explorable
 * heatmap plus this week's numbers, counted from the same series.
 */
import { computed } from 'vue'

import KCountUp from '@/components/ui/KCountUp.vue'
import KHeatmap from '@/components/ui/KHeatmap.vue'

const props = defineProps({
  series: { type: Array, required: true }, // [{ date, questions, completed, answered, ai_messages }]
})

const week = computed(() => props.series.slice(-7))
const sum = (days, field) => days.reduce((n, d) => n + d[field], 0)
const stats = computed(() => [
  { label: 'This week', value: sum(week.value, 'questions'), unit: 'questions' },
  { label: 'Active days', value: week.value.filter((d) => d.questions > 0).length, unit: 'of 7' },
  { label: 'Last 90 days', value: sum(props.series, 'completed'), unit: 'completed' },
])
const empty = computed(() => props.series.every((d) => d.questions === 0))
</script>

<template>
  <div>
    <KHeatmap :series="series" interactive :cell="16" label="Questions practised per day, last 90 days" />
    <p v-if="empty" class="mt-2 text-sm text-muted">Your first day of practice will light up the last square.</p>
    <dl class="mt-8 grid grid-cols-3 gap-4 border-t border-rule-soft pt-6">
      <div v-for="s in stats" :key="s.label">
        <dt class="k-eyebrow text-muted">{{ s.label }}</dt>
        <dd class="mt-2">
          <span class="k-serif text-4xl"><KCountUp :value="s.value" /></span>
          <span class="ml-1.5 text-sm text-muted">{{ s.unit }}</span>
        </dd>
      </div>
    </dl>
  </div>
</template>
