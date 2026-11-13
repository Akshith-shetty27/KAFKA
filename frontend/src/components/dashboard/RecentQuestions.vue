<script setup>
import KDifficulty from '@/components/ui/KDifficulty.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import { timeAgo } from '@/utils/format'

defineProps({
  records: { type: Array, required: true },
})
</script>

<template>
  <ul v-if="records.length">
    <li
      v-for="(r, i) in records"
      :key="r.question.slug"
      class="grid grid-cols-[1fr_auto] items-center gap-x-6 gap-y-2 py-4 sm:grid-cols-[minmax(0,1fr)_9rem_8rem_7rem]"
      :class="i > 0 ? 'border-t border-rule-soft' : ''"
    >
      <div class="min-w-0">
        <p class="truncate font-medium">{{ r.question.title }}</p>
        <p class="mt-1 truncate text-sm text-muted">{{ r.question.category.name }} · {{ r.question.topic.name }}</p>
      </div>
      <KDifficulty :level="r.question.difficulty" class="hidden sm:inline-flex" />
      <span
        class="k-eyebrow inline-flex items-center gap-2"
        :class="r.status === 'completed' ? 'text-accent-text' : 'text-muted'"
      >
        <span class="size-2" :class="r.status === 'completed' ? 'bg-accent' : 'border border-current'" aria-hidden="true" />
        {{ r.status }}
      </span>
      <span class="hidden text-right text-sm text-muted sm:block">{{ timeAgo(r.updated_at) }}</span>
    </li>
  </ul>
  <KEmptyState v-else title="No questions yet">
    Questions you open or answer will appear here, so you can pick up where you left off.
  </KEmptyState>
</template>
