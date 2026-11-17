<script setup>
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KProgressRing from '@/components/ui/KProgressRing.vue'

defineProps({
  topics: { type: Array, required: true },
})
</script>

<template>
  <ul v-if="topics.length" class="flex flex-col gap-4">
    <li v-for="topic in topics" :key="topic.slug">
      <RouterLink
        :to="{ name: 'practice', params: { category: topic.category.slug }, query: { topic: topic.slug } }"
        class="k-lift group flex items-center gap-5 border border-rule-soft bg-surface p-5 hover:border-rule"
      >
        <KProgressRing :value="topic.completed_count" :max="topic.question_count" :label="`${topic.name} progress`" :size="52">
          <span class="font-mono text-[11px]">{{ topic.completed_count }}</span>
        </KProgressRing>
        <div class="min-w-0 flex-1">
          <p class="k-eyebrow truncate text-[10px] text-muted">
            {{ topic.category.name }}<template v-if="topic.section"> · {{ topic.section.name }}</template>
          </p>
          <h3 class="mt-1.5 truncate text-lg font-medium tracking-tight group-hover:text-accent-text">{{ topic.name }}</h3>
          <p class="mt-0.5 text-sm text-muted">
            {{ topic.attempted_count > 0 ? 'In progress — finish what you started' : 'Next up in the curriculum' }} ·
            <span class="font-mono">{{ topic.completed_count }}/{{ topic.question_count }}</span>
          </p>
        </div>
      </RouterLink>
    </li>
  </ul>
  <KEmptyState v-else title="Every topic complete" glyph="◎">Nothing left to recommend — impressive.</KEmptyState>
</template>
