<script setup>
/** Renders trusted-or-not Markdown safely (see utils/markdown.js). */
import { computed } from 'vue'

import { copyText } from '@/utils/clipboard'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
  source: { type: String, default: '' },
  size: { type: String, default: 'base' }, // base | lg
})

const html = computed(() => renderMarkdown(props.source))

// Copy buttons on code blocks are plain HTML (rendered with the markdown), so
// one delegated listener handles them all — including while a reply streams.
async function onClick(event) {
  const button = event.target.closest('[data-copy-code]')
  if (!button) return
  const code = button.closest('.k-code-block')?.querySelector('pre')?.innerText ?? ''
  const ok = await copyText(code)
  button.textContent = ok ? 'Copied' : 'Copy failed'
  setTimeout(() => (button.textContent = 'Copy'), 1600)
}
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- sanitised by DOMPurify -->
  <div class="k-prose" :class="size === 'lg' ? 'k-prose-lg' : ''" @click="onClick" v-html="html" />
</template>
