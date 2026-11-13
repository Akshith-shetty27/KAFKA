<script setup>
import KProgressBar from '@/components/ui/KProgressBar.vue'
import { percent } from '@/utils/format'

defineProps({
  categories: { type: Array, required: true },
})
</script>

<template>
  <ul class="flex flex-col">
    <li
      v-for="(cat, i) in categories"
      :key="cat.slug"
      class="grid grid-cols-[3.5rem_1fr] items-center gap-5 py-5"
      :class="i > 0 ? 'border-t border-rule-soft' : ''"
    >
      <span class="k-serif text-center text-4xl leading-none not-italic" aria-hidden="true">{{ cat.glyph }}</span>
      <div class="min-w-0">
        <div class="flex items-baseline justify-between gap-4">
          <h3 class="font-medium tracking-tight uppercase">{{ cat.name }}</h3>
          <span class="font-mono text-sm text-muted">
            {{ cat.completed_count }}<span class="text-muted/60">/{{ cat.question_count }}</span>
          </span>
        </div>
        <div class="mt-3">
          <KProgressBar :value="cat.completed_count" :max="cat.question_count" :label="`${cat.name} progress`" />
        </div>
        <p class="mt-2.5 text-sm text-muted">
          {{ cat.attempted_count }} attempted
          <template v-if="cat.answers_total">
            · {{ percent(cat.answers_correct / cat.answers_total) }} MCQ accuracy
          </template>
        </p>
      </div>
    </li>
  </ul>
</template>
