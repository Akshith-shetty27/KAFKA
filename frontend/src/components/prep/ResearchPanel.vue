<script setup>
/**
 * What KAFKA found on the web about the company's past interviews: the rounds
 * in order, the topics most often asked, and which sites it came from — named
 * in plain text, never linked, so students stay inside KAFKA.
 */
import { computed } from 'vue'

const props = defineProps({
  research: { type: Object, default: () => ({}) },
  company: { type: String, default: '' },
})

const has = computed(() => Boolean(props.research && (props.research.rounds?.length || props.research.summary)))
const heading = computed(() => {
  if (props.research?.basis === 'company') return `How ${props.research.company_found || props.company} interviews`
  if (props.company) return `How companies like ${props.company} interview`
  return 'How companies interview for this role'
})
const note = computed(() => {
  if (props.research?.basis !== 'similar' || !props.company) return ''
  const found = props.research.company_found
  return found
    ? `No interview reports turned up for ${props.company}, so this is based on ${found} and similar companies.`
    : `No interview reports turned up for ${props.company}, so this is based on similar companies.`
})
function listOf(names) {
  if (names.length < 2) return names.join('')
  return `${names.slice(0, -1).join(', ')} and ${names.at(-1)}`
}
</script>

<template>
  <section v-if="has" class="mt-10 border border-rule-soft bg-surface p-6 sm:p-8" aria-labelledby="research-title">
    <div class="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-2">
      <h2 id="research-title" class="text-2xl font-medium tracking-tight">{{ heading }}</h2>
      <p class="k-eyebrow text-[11px] text-muted">From past interview experiences</p>
    </div>
    <p v-if="note" class="mt-3 text-sm text-warning">{{ note }}</p>
    <p v-if="research.summary" class="mt-3 max-w-3xl leading-relaxed text-muted">{{ research.summary }}</p>

    <ol v-if="research.rounds?.length" class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4" aria-label="Interview rounds">
      <li v-for="(round, i) in research.rounds" :key="i" class="flex flex-col gap-2 border-t-2 border-accent bg-raised p-4">
        <p class="k-eyebrow text-[10px] text-muted">Round {{ i + 1 }}</p>
        <p class="font-medium">{{ round.name }}</p>
        <p v-if="round.details" class="text-sm leading-relaxed text-muted">{{ round.details }}</p>
      </li>
    </ol>

    <div v-if="research.frequently_asked?.length" class="mt-6">
      <p class="k-eyebrow text-[11px]">Asked most often</p>
      <ul class="mt-3 flex flex-wrap gap-2">
        <li v-for="topic in research.frequently_asked" :key="topic" class="border border-rule-soft px-2.5 py-1 text-sm">{{ topic }}</li>
      </ul>
    </div>

    <p v-if="research.sources?.length" class="mt-6 text-xs text-muted">
      Based on interview experiences shared on {{ listOf(research.sources) }}.
    </p>
  </section>
</template>
