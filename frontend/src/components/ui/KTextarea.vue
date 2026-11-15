<script setup>
/** Multi-line counterpart of KInput (same label, hint, error and focus styles). */
import { computed, useId } from 'vue'

const model = defineModel({ type: String, default: '' })

const props = defineProps({
  label: { type: String, required: true },
  error: { type: [String, Array], default: null },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 6 },
  maxlength: { type: Number, default: undefined },
  showCount: { type: Boolean, default: false },
})

const id = useId()
const errorText = computed(() => (Array.isArray(props.error) ? props.error[0] : props.error))
const describedBy = computed(() => [errorText.value && `${id}-error`, props.hint && `${id}-hint`].filter(Boolean).join(' ') || undefined)
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-baseline justify-between gap-4">
      <label :for="id" class="k-eyebrow text-muted">
        {{ label }}<span v-if="required" class="text-accent-text" aria-hidden="true"> *</span>
      </label>
      <span v-if="showCount" class="font-mono text-xs text-muted" aria-live="polite">
        {{ model.length.toLocaleString() }}<template v-if="maxlength"> / {{ maxlength.toLocaleString() }}</template>
      </span>
    </div>
    <textarea
      :id="id"
      v-model="model"
      :rows="rows"
      :required="required"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :aria-invalid="errorText ? 'true' : undefined"
      :aria-describedby="describedBy"
      class="w-full resize-y rounded-[2px] border bg-transparent px-3.5 py-3 font-sans text-base leading-relaxed text-fg transition-colors outline-none placeholder:text-muted/70 focus:border-accent"
      :class="errorText ? 'border-danger' : 'border-rule-soft hover:border-muted'"
    />
    <p v-if="errorText" :id="`${id}-error`" class="text-sm text-danger">{{ errorText }}</p>
    <p v-else-if="hint" :id="`${id}-hint`" class="text-sm text-muted">{{ hint }}</p>
  </div>
</template>
