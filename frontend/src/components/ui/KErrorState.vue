<script setup>
import KIcon from './KIcon.vue'

defineProps({
  message: { type: String, default: 'Something went wrong.' },
  retryable: { type: Boolean, default: true },
})
defineEmits(['retry'])
</script>

<template>
  <div class="flex flex-wrap items-center gap-x-4 gap-y-2 border border-danger/40 px-4 py-3 text-sm" role="alert">
    <KIcon name="alert" class="text-danger" />
    <span class="flex-1">{{ message }}</span>
    <button
      v-if="retryable"
      type="button"
      class="k-label inline-flex items-center gap-2 text-xs hover:text-accent-text"
      @click="$emit('retry')"
    >
      <KIcon name="refresh" :size="14" /> Retry
    </button>
  </div>
</template>
