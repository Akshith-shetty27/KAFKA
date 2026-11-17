<script setup>
/** "Copy" button with a short "Copied" confirmation (announced politely to screen readers). */
import { ref } from 'vue'

import { copyText } from '@/utils/clipboard'

import KIcon from './KIcon.vue'

const props = defineProps({
  text: { type: String, required: true },
  label: { type: String, default: 'Copy' },
})

const state = ref('idle') // idle | copied | failed
let timer = null
async function copy() {
  state.value = (await copyText(props.text)) ? 'copied' : 'failed'
  clearTimeout(timer)
  timer = setTimeout(() => (state.value = 'idle'), 1600)
}
</script>

<template>
  <button type="button" class="flex items-center gap-2 py-3 text-xs tracking-wider text-paper-50/60 uppercase transition-colors hover:text-accent" @click="copy">
    <KIcon :name="state === 'copied' ? 'check' : 'copy'" :size="14" />
    <span aria-live="polite">{{ state === 'copied' ? 'Copied' : state === 'failed' ? 'Copy failed' : label }}</span>
  </button>
</template>
