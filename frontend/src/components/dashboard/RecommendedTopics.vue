<script setup>
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KProgressBar from '@/components/ui/KProgressBar.vue'

defineProps({
  topics: { type: Array, required: true },
})
</script>

<template>
  <ul v-if="topics.length" class="flex flex-col gap-4">
    <li v-for="topic in topics" :key="topic.slug" class="bg-surface p-5">
      <p class="k-eyebrow text-muted">{{ topic.category.name }}<template v-if="topic.section"> · {{ topic.section.name }}</template></p>
      <div class="mt-3 flex items-baseline justify-between gap-4">
        <h3 class="text-xl font-medium tracking-tight">{{ topic.name }}</h3>
        <span class="font-mono text-sm text-muted">{{ topic.completed_count }}/{{ topic.question_count }}</span>
      </div>
      <p class="mt-1 text-sm text-muted">{{ topic.attempted_count > 0 ? 'In progress — finish what you started' : 'Next up in the curriculum' }}</p>
      <div class="mt-4">
        <KProgressBar :value="topic.completed_count" :max="topic.question_count" :label="`${topic.name} progress`" />
      </div>
    </li>
  </ul>
  <KEmptyState v-else title="Every topic complete" glyph="◎">Nothing left to recommend — impressive.</KEmptyState>
</template>
