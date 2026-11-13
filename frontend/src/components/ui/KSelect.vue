<script setup>
import { computed, useId } from 'vue'

const model = defineModel({ type: [String, Number], default: '' })

const props = defineProps({
  label: { type: String, required: true },
  /** [{ value, label }] or plain strings */
  options: { type: Array, required: true },
  error: { type: [String, Array], default: null },
  hint: { type: String, default: '' },
})

const id = useId()
const errorText = computed(() => (Array.isArray(props.error) ? props.error[0] : props.error))
const normalised = computed(() => props.options.map((o) => (typeof o === 'object' ? o : { value: o, label: o })))
</script>

<template>
  <div class="flex flex-col gap-2">
    <label :for="id" class="k-eyebrow text-muted">{{ label }}</label>
    <div class="relative">
      <select
        :id="id"
        v-model="model"
        :aria-invalid="errorText ? 'true' : undefined"
        class="h-12 w-full appearance-none rounded-[2px] border bg-canvas px-3.5 pr-10 font-sans text-base text-fg outline-none focus:border-accent"
        :class="errorText ? 'border-danger' : 'border-rule-soft hover:border-muted'"
      >
        <option v-for="o in normalised" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
      <span class="pointer-events-none absolute inset-y-0 right-3.5 flex items-center text-muted" aria-hidden="true">▾</span>
    </div>
    <p v-if="errorText" class="text-sm text-danger">{{ errorText }}</p>
    <p v-else-if="hint" class="text-sm text-muted">{{ hint }}</p>
  </div>
</template>
