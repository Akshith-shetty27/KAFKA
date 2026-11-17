<script setup>
/**
 * Year-at-a-glance activity grid: one column per week (Monday first), one
 * square per day, teal intensity by number of questions practised.
 * series: [{ date: 'YYYY-MM-DD', questions, completed?, answered? }] oldest → newest (zero-filled).
 *
 * `interactive`: one keyboard tab stop for the whole grid (arrow keys move
 * between days, Home/End jump to the ends); hovering or clicking a square
 * selects it, and a readout below announces the selected day's numbers.
 */
import { computed, ref, useId, watch } from 'vue'

import { longDate } from '@/utils/format'

const props = defineProps({
  series: { type: Array, required: true },
  label: { type: String, default: 'Questions practised per day' },
  interactive: { type: Boolean, default: false },
  /** Square size in px (gap stays 3px). */
  cell: { type: Number, default: 11 },
})

const cellStyle = computed(() => ({ width: `${props.cell}px`, height: `${props.cell}px` }))

const labelId = useId()
const selected = ref(props.series.length - 1)
watch(
  () => props.series.length,
  (n) => (selected.value = n - 1),
)
const selectedDay = computed(() => props.series[selected.value] ?? null)

function select(day) {
  if (props.interactive && day) selected.value = props.series.indexOf(day)
}

function onKey(event) {
  const step = { ArrowLeft: -7, ArrowRight: 7, ArrowUp: -1, ArrowDown: 1 }[event.key]
  let next = selected.value
  if (step !== undefined) next += step
  else if (event.key === 'Home') next = 0
  else if (event.key === 'End') next = props.series.length - 1
  else return
  event.preventDefault()
  selected.value = Math.min(props.series.length - 1, Math.max(0, next))
}

const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`

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
  <figure :aria-label="interactive ? undefined : summary" :role="interactive ? undefined : 'img'">
    <p v-if="interactive" :id="labelId" class="sr-only">{{ summary }} Use the arrow keys to move between days.</p>
    <div class="overflow-x-auto pb-2">
      <div class="inline-flex flex-col gap-1.5">
        <div class="flex gap-[3px] pl-8 font-mono text-[10px] text-muted" aria-hidden="true">
          <span v-for="(m, i) in monthLabels" :key="i" class="overflow-visible whitespace-nowrap" :style="{ width: `${cell}px` }">{{ m }}</span>
        </div>
        <div
          class="flex gap-[3px] outline-offset-4"
          :tabindex="interactive ? 0 : undefined"
          :role="interactive ? 'group' : undefined"
          :aria-labelledby="interactive ? labelId : undefined"
          @keydown="interactive && onKey($event)"
        >
          <div class="flex w-7 flex-col gap-[3px] font-mono text-[10px] text-muted" aria-hidden="true">
            <span v-for="(d, i) in ['Mon', '', 'Wed', '', 'Fri', '', '']" :key="i" class="flex items-center" :style="cellStyle">{{ d }}</span>
          </div>
          <div v-for="(week, w) in weeks" :key="w" class="flex flex-col gap-[3px]">
            <span
              v-for="(day, r) in week"
              :key="r"
              class="transition-[outline-color]"
              :style="cellStyle"
              :class="[
                day ? LEVEL_CLASS[level(day.questions)] : 'bg-transparent',
                interactive && day && series.indexOf(day) === selected ? 'outline-2 outline-offset-1 outline-fg' : '',
                interactive && day ? 'cursor-pointer' : '',
              ]"
              :title="day ? `${longDate(day.date)}: ${plural(day.questions, 'question')}` : undefined"
              @mouseenter="select(day)"
              @click="select(day)"
            />
          </div>
        </div>
      </div>
    </div>
    <p v-if="interactive && selectedDay" class="mt-4 min-h-[1.5rem] text-sm" aria-live="polite">
      <span class="font-medium">{{ longDate(selectedDay.date) }}</span>
      <span class="text-muted">
        · {{ plural(selectedDay.questions, 'question') }} practised<template v-if="selectedDay.completed !== undefined">
          · {{ selectedDay.completed }} completed · {{ plural(selectedDay.answered ?? 0, 'answer') }}</template>
      </span>
    </p>
    <figcaption class="mt-3 flex items-center justify-end gap-2 font-mono text-[10px] text-muted" aria-hidden="true">
      Less
      <span v-for="c in LEVEL_CLASS" :key="c" class="size-[11px]" :class="c" />
      More
    </figcaption>
  </figure>
</template>
