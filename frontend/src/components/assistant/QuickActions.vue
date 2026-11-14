<script setup>
/**
 * One-click requests for a question: escalating hints, explain the solution,
 * review an MCQ answer. Which ones are offered follows the same rules the
 * server enforces (`capabilities`).
 */
import { computed } from 'vue'

const props = defineProps({
  capabilities: { type: Object, required: true }, // { hint, explain, review }
  hintsUsed: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['action'])

const nextHint = computed(() => Math.min(3, props.hintsUsed + 1))
const HINT_PROMPTS = {
  1: "I'm stuck. Give me a small nudge.",
  2: 'Still stuck. What is the key insight?',
  3: 'Walk me through the steps, without giving me the final code.',
}

const actions = computed(() => {
  const list = []
  if (props.capabilities.hint && props.hintsUsed < 3) {
    list.push({ key: 'hint', label: `Hint ${nextHint.value} of 3`, mode: 'hint', hintLevel: nextHint.value, content: HINT_PROMPTS[nextHint.value] })
  }
  if (props.capabilities.review) {
    list.push({ key: 'review', label: 'Review my answer', mode: 'review', content: 'Why is the correct answer correct, and where did my reasoning go wrong?' })
  }
  if (props.capabilities.explain) {
    list.push({ key: 'explain', label: 'Explain the solution', mode: 'explain', content: 'Explain the solution step by step.' })
  }
  return list
})
</script>

<template>
  <div v-if="actions.length" class="flex flex-wrap gap-2" role="group" aria-label="Quick requests">
    <button
      v-for="a in actions"
      :key="a.key"
      type="button"
      class="k-eyebrow border px-3 py-2 text-[11px] tracking-[0.15em] transition-colors disabled:opacity-40"
      :class="a.key === 'hint' ? 'border-accent text-accent-text hover:bg-accent hover:text-on-accent' : 'border-rule-soft hover:border-fg'"
      :disabled="disabled"
      @click="emit('action', a)"
    >
      {{ a.label }}
    </button>
  </div>
</template>
