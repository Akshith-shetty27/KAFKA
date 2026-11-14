<script setup>
import { computed } from 'vue'

import KChecklist from '@/components/ui/KChecklist.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'

const props = defineProps({
  plan: { type: Object, required: true },
})

const items = computed(() => {
  let nextMarked = false
  return props.plan.items.map(({ question, done }) => {
    let tag = done ? 'Done' : ''
    if (!done && !nextMarked) {
      tag = 'Next'
      nextMarked = true
    }
    return {
      key: question.slug,
      label: question.title,
      meta: `${question.category.name} · ${question.topic.name} · ${question.difficulty}`,
      done,
      tag,
      to: { name: 'question', params: { slug: question.slug } },
    }
  })
})
</script>

<template>
  <KChecklist v-if="items.length" :items="items" />
  <KEmptyState v-else title="Nothing left to plan" glyph="✓">
    You've completed every question in the bank. New questions are added regularly.
  </KEmptyState>
</template>
