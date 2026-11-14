<script setup>
/**
 * Highlighted code with a language label and a copy button. With several
 * `solutions` it shows language tabs.
 */
import { computed, ref, watch } from 'vue'

import { highlight } from '@/utils/markdown'

import KIcon from './KIcon.vue'

const props = defineProps({
  /** [{ language, code }] */
  solutions: { type: Array, required: true },
})

const LABELS = { python: 'Python', java: 'Java', cpp: 'C++', javascript: 'JavaScript', sql: 'SQL' }
const active = ref(props.solutions[0]?.language)
watch(
  () => props.solutions,
  (list) => {
    if (!list.some((s) => s.language === active.value)) active.value = list[0]?.language
  },
)

const current = computed(() => props.solutions.find((s) => s.language === active.value) ?? props.solutions[0])
const html = computed(() => (current.value ? highlight(current.value.code, current.value.language) : ''))
const lineCount = computed(() => (current.value?.code.split('\n').length ?? 0))

const copied = ref(false)
async function copy() {
  try {
    await navigator.clipboard.writeText(current.value.code)
    copied.value = true
    setTimeout(() => (copied.value = false), 1600)
  } catch {
    copied.value = false
  }
}
</script>

<template>
  <figure v-if="current" data-surface="ink" class="border border-ink-700 font-mono text-[13px] sm:text-sm">
    <div class="flex items-center justify-between gap-4 border-b border-ink-700 px-4">
      <div class="flex" role="tablist" aria-label="Solution language">
        <button
          v-for="s in solutions"
          :key="s.language"
          type="button"
          role="tab"
          :aria-selected="s.language === active"
          class="-mb-px border-b-2 px-3 py-3 text-xs tracking-wider uppercase transition-colors"
          :class="s.language === active ? 'border-accent text-paper-50' : 'border-transparent text-paper-50/50 hover:text-paper-50'"
          @click="active = s.language"
        >
          {{ LABELS[s.language] ?? s.language }}
        </button>
      </div>
      <button type="button" class="flex items-center gap-2 py-3 text-xs tracking-wider text-paper-50/60 uppercase hover:text-accent" @click="copy">
        <KIcon :name="copied ? 'check' : 'copy'" :size="14" />
        <span aria-live="polite">{{ copied ? 'Copied' : 'Copy' }}</span>
      </button>
    </div>
    <div class="flex overflow-x-auto">
      <div class="shrink-0 py-5 pr-4 pl-5 text-right leading-[1.85] text-paper-50/25 select-none" aria-hidden="true">
        <div v-for="n in lineCount" :key="n">{{ n }}</div>
      </div>
      <!-- eslint-disable-next-line vue/no-v-html -- highlight.js output escapes the code -->
      <pre class="k-code-plain py-5 pr-6 leading-[1.85]"><code class="hljs" v-html="html" /></pre>
    </div>
  </figure>
</template>
