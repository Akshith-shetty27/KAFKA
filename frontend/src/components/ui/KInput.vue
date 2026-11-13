<script setup>
import { computed, ref, useId } from 'vue'

import KIcon from './KIcon.vue'

const model = defineModel({ type: [String, Number], default: '' })

const props = defineProps({
  label: { type: String, required: true },
  type: { type: String, default: 'text' },
  error: { type: [String, Array], default: null },
  hint: { type: String, default: '' },
  autocomplete: { type: String, default: undefined },
  required: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  inputmode: { type: String, default: undefined },
  min: { type: [Number, String], default: undefined },
  max: { type: [Number, String], default: undefined },
})

const id = useId()
const revealed = ref(false)
const errorText = computed(() => (Array.isArray(props.error) ? props.error[0] : props.error))
const inputType = computed(() => (props.type === 'password' && revealed.value ? 'text' : props.type))
const describedBy = computed(() => [errorText.value && `${id}-error`, props.hint && `${id}-hint`].filter(Boolean).join(' ') || undefined)
</script>

<template>
  <div class="flex flex-col gap-2">
    <label :for="id" class="k-eyebrow text-muted">
      {{ label }}<span v-if="required" class="text-accent-text" aria-hidden="true"> *</span>
    </label>
    <div class="relative">
      <input
        :id="id"
        v-model="model"
        :type="inputType"
        :autocomplete="autocomplete"
        :required="required"
        :placeholder="placeholder"
        :inputmode="inputmode"
        :min="min"
        :max="max"
        :aria-invalid="errorText ? 'true' : undefined"
        :aria-describedby="describedBy"
        class="h-12 w-full rounded-[2px] border bg-transparent px-3.5 font-sans text-base text-fg transition-colors outline-none placeholder:text-muted/70 focus:border-accent"
        :class="[errorText ? 'border-danger' : 'border-rule-soft hover:border-muted', type === 'password' ? 'pr-12' : '']"
      />
      <button
        v-if="type === 'password'"
        type="button"
        class="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-muted hover:text-fg"
        :aria-label="revealed ? 'Hide password' : 'Show password'"
        :aria-pressed="revealed"
        @click="revealed = !revealed"
      >
        <KIcon :name="revealed ? 'eye-off' : 'eye'" />
      </button>
    </div>
    <p v-if="errorText" :id="`${id}-error`" class="text-sm text-danger">{{ errorText }}</p>
    <p v-else-if="hint" :id="`${id}-hint`" class="text-sm text-muted">{{ hint }}</p>
  </div>
</template>
