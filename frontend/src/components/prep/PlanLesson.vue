<script setup>
/**
 * A plan item KAFKA's question bank doesn't cover yet, taught inside KAFKA:
 * short notes, points to remember and a 5-question quiz. The lesson is written
 * by the AI on first open (a few seconds), stored on the item, and reused.
 */
import { computed, reactive, ref } from 'vue'

import KIcon from '@/components/ui/KIcon.vue'
import KMarkdown from '@/components/ui/KMarkdown.vue'
import { useToast } from '@/composables/useToast'
import { toApiError } from '@/services/http'
import { prepApi } from '@/services/prep.api'

const props = defineProps({
  planId: { type: Number, required: true },
  item: { type: Object, required: true },
})
const emit = defineEmits(['loaded'])

const toast = useToast()
const open = ref(false)
const loading = ref(false)
const error = ref(null)
const lesson = computed(() => props.item.lesson)
// The option the student picked for each quiz question (index), once they answer.
const picked = reactive({})
const score = computed(() => (lesson.value?.quiz ?? []).filter((q, i) => picked[i] === q.answer).length)
const answered = computed(() => Object.keys(picked).length)

async function start() {
  if (lesson.value) {
    open.value = !open.value
    return
  }
  loading.value = true
  error.value = null
  try {
    const { lesson: data } = await prepApi.lesson(props.planId, props.item.id)
    emit('loaded', data)
    open.value = true
  } catch (err) {
    error.value = err.apiError ?? toApiError(err)
    toast.error(`Couldn't prepare the lesson: ${error.value.message}`)
  } finally {
    loading.value = false
  }
}

function choose(qIndex, option) {
  if (picked[qIndex] === undefined) picked[qIndex] = option
}
function optionClass(q, qIndex, o) {
  if (picked[qIndex] === undefined) return 'border-rule-soft hover:border-accent'
  if (o === q.answer) return 'border-accent bg-accent/10'
  if (o === picked[qIndex]) return 'border-danger bg-danger/10'
  return 'border-rule-soft opacity-60'
}
</script>

<template>
  <div class="mt-5 border-t border-rule-soft pt-4">
    <button
      type="button"
      class="k-label inline-flex items-center gap-2 bg-accent px-4 py-2.5 text-[11px] text-on-accent transition-[filter] hover:brightness-95 disabled:opacity-60"
      :aria-expanded="open"
      :disabled="loading"
      @click="start"
    >
      <template v-if="loading">Writing your lesson…</template>
      <template v-else-if="!lesson">Learn it here</template>
      <template v-else>{{ open ? 'Hide lesson' : 'Open lesson' }}</template>
      <KIcon name="chevron-right" :size="12" class="transition-transform" :class="open ? '-rotate-90' : 'rotate-90'" />
    </button>
    <p v-if="!lesson && !loading" class="mt-2 text-xs text-muted">KAFKA writes short notes and a quiz for this — no need to leave the site.</p>

    <div v-if="open && lesson" class="mt-6 flex flex-col gap-6">
      <p class="text-xs text-muted">Written by KAFKA's AI for this plan. Double-check anything that matters before your interview.</p>

      <section v-for="(sec, i) in lesson.sections" :key="i">
        <h5 class="font-medium">{{ sec.heading }}</h5>
        <KMarkdown :source="sec.body" class="mt-2 text-sm leading-relaxed text-muted" />
      </section>

      <section v-if="lesson.key_points.length" class="border-l-2 border-accent pl-4">
        <h5 class="k-eyebrow text-[11px]">Remember</h5>
        <ul class="mt-3 flex flex-col gap-1.5 text-sm">
          <li v-for="(point, i) in lesson.key_points" :key="i" class="flex gap-2">
            <span class="text-accent-text" aria-hidden="true">·</span><KMarkdown :source="point" class="min-w-0" />
          </li>
        </ul>
      </section>

      <section aria-label="Quiz">
        <div class="flex items-baseline justify-between gap-4">
          <h5 class="k-eyebrow text-[11px]">Quick quiz</h5>
          <p class="font-mono text-xs text-muted" aria-live="polite">{{ score }} of {{ lesson.quiz.length }} correct · {{ answered }} answered</p>
        </div>
        <ol class="mt-4 flex flex-col gap-6">
          <li v-for="(q, qi) in lesson.quiz" :key="qi">
            <p class="text-sm font-medium">{{ qi + 1 }}. {{ q.question }}</p>
            <div class="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2" role="group" :aria-label="`Question ${qi + 1} options`">
              <button
                v-for="(opt, oi) in q.options"
                :key="oi"
                type="button"
                class="border px-3 py-2 text-left text-sm transition-colors"
                :class="optionClass(q, qi, oi)"
                :aria-pressed="picked[qi] === oi"
                :disabled="picked[qi] !== undefined"
                @click="choose(qi, oi)"
              >
                {{ opt }}
              </button>
            </div>
            <p v-if="picked[qi] !== undefined" class="mt-2 text-sm" :class="picked[qi] === q.answer ? 'text-accent-text' : 'text-danger'">
              {{ picked[qi] === q.answer ? 'Correct.' : `Not quite — it's “${q.options[q.answer]}”.` }}
              <span class="text-muted">{{ q.explanation }}</span>
            </p>
          </li>
        </ol>
      </section>
    </div>
  </div>
</template>
