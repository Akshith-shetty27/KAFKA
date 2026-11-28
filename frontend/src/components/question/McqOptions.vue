<script setup>
/**
 * Multiple-choice options as real radio inputs (keyboard + screen reader
 * support for free). Before answering: pick one, then "Check answer".
 * After answering, `result` paints the correct option teal and a wrong pick
 * red. The correct answer only exists on the client after the server has
 * graded the submission.
 */
import { computed, ref, useId, watch } from 'vue'

import KButton from '@/components/ui/KButton.vue'
import KIcon from '@/components/ui/KIcon.vue'

const props = defineProps({
  options: { type: Array, required: true }, // [{ id, label, text }]
  /** null, or { selectedId, correctId } once answered */
  result: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const name = useId()
const selected = ref(props.result?.selectedId ?? null)
// True only right after this page graded an answer — drives the pop/shake once.
const justAnswered = ref(false)
watch(
  () => props.result,
  (r, before) => {
    selected.value = r?.selectedId ?? null
    justAnswered.value = Boolean(r && !before)
  },
)

const answered = computed(() => props.result !== null)

function stateOf(option) {
  if (!answered.value) return selected.value === option.id ? 'selected' : 'idle'
  if (option.id === props.result.correctId) return 'correct'
  if (option.id === props.result.selectedId) return 'wrong'
  return 'dim'
}
</script>

<template>
  <form @submit.prevent="selected && emit('submit', selected)">
    <fieldset :disabled="answered || submitting">
      <legend class="sr-only">Choose one answer</legend>
      <div class="flex flex-col gap-3">
        <label
          v-for="option in options"
          :key="option.id"
          class="flex cursor-pointer items-start gap-4 border p-4 transition-colors has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-accent"
          :class="{
            'border-rule-soft hover:border-muted': stateOf(option) === 'idle',
            'border-fg': stateOf(option) === 'selected',
            'border-accent bg-accent/10': stateOf(option) === 'correct',
            'border-danger bg-danger/10': stateOf(option) === 'wrong',
            'cursor-default border-rule-soft opacity-60': stateOf(option) === 'dim',
            'k-pop': justAnswered && stateOf(option) === 'correct',
            'k-shake': justAnswered && stateOf(option) === 'wrong',
          }"
        >
          <input v-model="selected" type="radio" :name="name" :value="option.id" class="sr-only" />
          <span
            class="flex size-7 shrink-0 items-center justify-center font-mono text-sm"
            :class="{
              'border border-rule-soft': ['idle', 'dim'].includes(stateOf(option)),
              'bg-fg text-canvas': stateOf(option) === 'selected',
              'bg-accent text-on-accent': stateOf(option) === 'correct',
              'bg-danger text-paper-50': stateOf(option) === 'wrong',
            }"
            aria-hidden="true"
          >
            <KIcon v-if="stateOf(option) === 'correct'" name="check" :size="16" />
            <KIcon v-else-if="stateOf(option) === 'wrong'" name="x" :size="16" />
            <template v-else>{{ option.label }}</template>
          </span>
          <span class="pt-0.5 text-[1.0625rem] leading-relaxed">{{ option.text }}</span>
          <span v-if="stateOf(option) === 'correct'" class="sr-only">(correct answer)</span>
          <span v-if="stateOf(option) === 'wrong'" class="sr-only">(your answer — incorrect)</span>
        </label>
      </div>
    </fieldset>
    <KButton v-if="!answered" type="submit" class="mt-6" :disabled="!selected" :loading="submitting" icon="arrow-right">
      Check answer
    </KButton>
  </form>
</template>
