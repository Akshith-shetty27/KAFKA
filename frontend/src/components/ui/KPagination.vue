<script setup>
import { computed } from 'vue'

import KIcon from './KIcon.vue'

const props = defineProps({
  page: { type: Number, required: true },
  count: { type: Number, required: true },
  pageSize: { type: Number, required: true },
})
const emit = defineEmits(['update:page'])

const pages = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)))
const from = computed(() => (props.count === 0 ? 0 : (props.page - 1) * props.pageSize + 1))
const to = computed(() => Math.min(props.count, props.page * props.pageSize))
</script>

<template>
  <nav v-if="count > 0" class="flex flex-wrap items-center justify-between gap-4" aria-label="Pagination">
    <p class="k-eyebrow text-muted">{{ from }}–{{ to }} of {{ count }}</p>
    <div v-if="pages > 1" class="flex items-center gap-2">
      <button
        type="button"
        class="flex size-10 items-center justify-center border border-rule-soft hover:border-fg disabled:opacity-30 disabled:hover:border-rule-soft"
        :disabled="page <= 1"
        aria-label="Previous page"
        @click="emit('update:page', page - 1)"
      >
        <KIcon name="arrow-left" :size="16" />
      </button>
      <span class="font-mono text-sm tabular-nums">{{ page }} / {{ pages }}</span>
      <button
        type="button"
        class="flex size-10 items-center justify-center border border-rule-soft hover:border-fg disabled:opacity-30 disabled:hover:border-rule-soft"
        :disabled="page >= pages"
        aria-label="Next page"
        @click="emit('update:page', page + 1)"
      >
        <KIcon name="arrow-right" :size="16" />
      </button>
    </div>
  </nav>
</template>
