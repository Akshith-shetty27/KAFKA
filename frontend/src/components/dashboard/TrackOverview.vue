<script setup>
/**
 * One card per track the student prepares for. Aptitude is split into its
 * sections (Quantitative, Logical, Verbal) because placement tests score them
 * separately. Counts come from /topics/ (per-topic progress), summed here.
 * Each card links to the first unfinished topic of that track.
 */
import { computed } from 'vue'

import KTrackCard from '@/components/ui/KTrackCard.vue'

const props = defineProps({
  categories: { type: Array, required: true }, // summary.categories (order + glyphs)
  topics: { type: Array, required: true }, // /topics/ with progress
})

const SECTION_GLYPHS = { quantitative: '%', logical: '∴', verbal: 'Aa' }

const tracks = computed(() => {
  const out = []
  for (const category of props.categories) {
    const inCategory = props.topics.filter((t) => t.category.slug === category.slug)
    const groups = new Map()
    for (const topic of inCategory) {
      const key = topic.section?.slug ?? category.slug
      if (!groups.has(key)) {
        groups.set(key, {
          key,
          name: topic.section?.name ?? category.name,
          glyph: topic.section ? (SECTION_GLYPHS[topic.section.slug] ?? category.glyph) : category.glyph,
          category: category.slug,
          topics: [],
        })
      }
      groups.get(key).topics.push(topic)
    }
    for (const group of groups.values()) {
      const sum = (field) => group.topics.reduce((n, t) => n + t[field], 0)
      const nextTopic = group.topics.find((t) => t.completed_count < t.question_count) ?? group.topics[0]
      out.push({
        ...group,
        completed: sum('completed_count'),
        total: sum('question_count'),
        attempted: sum('attempted_count'),
        to: { name: 'practice', params: { category: group.category }, query: { topic: nextTopic.slug } },
      })
    }
  }
  return out
})
</script>

<template>
  <ul class="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-5">
    <li v-for="(track, i) in tracks" :key="track.key" v-reveal="{ delay: i * 0.06 }">
      <KTrackCard
        compact
        :to="track.to"
        :index="i + 1"
        :glyph="track.glyph"
        :name="track.name"
        :completed="track.completed"
        :total="track.total"
        :attempted="track.attempted"
      />
    </li>
  </ul>
</template>
