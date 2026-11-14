<script setup>
/** Renders trusted-or-not Markdown safely (see utils/markdown.js). */
import { computed } from 'vue'

import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
  source: { type: String, default: '' },
  size: { type: String, default: 'base' }, // base | lg
})

const html = computed(() => renderMarkdown(props.source))
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- sanitised by DOMPurify -->
  <div class="k-prose" :class="size === 'lg' ? 'k-prose-lg' : ''" v-html="html" />
</template>
