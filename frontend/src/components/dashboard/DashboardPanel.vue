<script setup>
/**
 * One dashboard section: eyebrow title, and its own loading / error state
 * so a single failing request doesn't blank the whole page.
 */
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'

defineProps({
  title: { type: String, required: true },
  index: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: Object, default: null },
  skeletonLines: { type: Number, default: 4 },
})
defineEmits(['retry'])
</script>

<template>
  <section class="flex flex-col">
    <header class="mb-6 flex items-baseline justify-between gap-4 border-b border-rule pb-4">
      <KEyebrow :index="index" as="h2">{{ title }}</KEyebrow>
      <slot name="aside" />
    </header>
    <KErrorState v-if="error" :message="error.message" @retry="$emit('retry')" />
    <KSkeleton v-else-if="loading" :lines="skeletonLines" height="1.25rem" />
    <slot v-else />
  </section>
</template>
