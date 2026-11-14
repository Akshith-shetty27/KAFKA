<script setup>
/**
 * Year-at-a-glance activity grid: one column per week (Monday first), one
 * square per day, teal intensity by number of questions practised.
 * series: [{ date: 'YYYY-MM-DD', questions }] oldest → newest (zero-filled).
 */
import { computed } from 'vue'

import { longDate } from '@/utils/format'

const props = defineProps({
  series: { type: Array, required: true },
  label: { type: String, default: 'Questions practised per day' },
})

const LEVEL_CLASS = ['bg-rule-soft', 'bg-accent/30', 'bg-accent/55', 'bg-accent/80', 'bg-accent']
function level(n) {
  if (n <= 0) return 0
  if (n <= 2) return 1
  if (n <= 5) return 2
  if (n <= 9) return 3
  return 4
}

const parse = (iso) => {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d)
}

/** weeks[col][row] — rows Monday..Sunday; null pads the first and last weeks. */
const weeks = computed(() => {
  if (!props.series.length) return []
  const firstWeekday = (parse(props.series[0].date).getDay() + 6) % 7 // Monday = 0
  const cells = [...Array(firstWeekday).fill(null), ...props.series]
  const out = []
  for (let i = 0; i < cells.length; i += 7) {
    const week = cells.slice(i, i + 7)
    while (week.length < 7) week.push(null)
    out.push(week)
  }
  return out
})

/** Month label above the first week that contains the 1st of a month. */
const monthLabels = computed(() =>
  weeks.value.map((week, i) => {
    const firstOfMonth = week.find((d) => d && d.date.endsWith('-01'))
    if (firstOfMonth) return parse(firstOfMonth.date).toLocaleDateString('en', { month: 'short' })
    return i === 0 && week.find(Boolean) ? parse(week.find(Boolean).date).toLocaleDateString('en', { month: 'short' }) : ''
  }),
)

const summary = computed(() => {
  const active = props.series.filter((d) => d.questions > 0)
  const best = active.reduce((b, d) => (d.questions > (b?.questions ?? 0) ? d : b), null)
  return `${props.label}: ${active.length} active days in the last ${props.series.length} days${
    best ? `; busiest day ${longDate(best.date)} with ${best.questions}` : ''
  }.`
})
</script>

<template>
  <figure :aria-label="summary" role="img">
    <div class="overflow-x-auto pb-2">
      <div class="inline-flex flex-col gap-1.5">
        <div class="flex gap-[3px] pl-8 font-mono text-[10px] text-muted" aria-hidden="true">
          <span v-for="(m, i) in monthLabels" :key="i" class="w-[11px] overflow-visible whitespace-nowrap">{{ m }}</span>
        </div>
        <div class="flex gap-[3px]">
          <div class="flex w-7 flex-col gap-[3px] font-mono text-[10px] leading-[11px] text-muted" aria-hidden="true">
            <span v-for="(d, i) in ['Mon', '', 'Wed', '', 'Fri', '', '']" :key="i" class="h-[11px]">{{ d }}</span>
          </div>
          <div v-for="(week, w) in weeks" :key="w" class="flex flex-col gap-[3px]">
            <span
              v-for="(day, r) in week"
              :key="r"
              class="size-[11px]"
              :class="day ? LEVEL_CLASS[level(day.questions)] : 'bg-transparent'"
              :title="day ? `${longDate(day.date)}: ${day.questions} question${day.questions === 1 ? '' : 's'}` : undefined"
            />
          </div>
        </div>
      </div>
    </div>
    <figcaption class="mt-3 flex items-center justify-end gap-2 font-mono text-[10px] text-muted" aria-hidden="true">
      Less
      <span v-for="c in LEVEL_CLASS" :key="c" class="size-[11px]" :class="c" />
      More
    </figcaption>
  </figure>
</template>
