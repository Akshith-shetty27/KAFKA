<script setup>
/**
 * Preparation hub ("Preparation Dashboard"): the three tracks with my
 * progress, then every topic grouped by track (and section for aptitude),
 * each linking into the practice library pre-filtered to that topic.
 */
import { computed, onMounted, ref } from 'vue'

import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KProgressBar from '@/components/ui/KProgressBar.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import KTrackCard from '@/components/ui/KTrackCard.vue'
import { useAsync } from '@/composables/useAsync'
import { useMotion } from '@/motion'
import { catalogApi } from '@/services/catalog.api'

const load = useAsync(async () => {
  const [categories, topics] = await Promise.all([catalogApi.categories(), catalogApi.topics()])
  return { categories, topics }
})
onMounted(load.run)

// Track cards rise in one after another once the data has arrived.
const trackGrid = ref(null)
useMotion(
  trackGrid,
  ({ q, gsap, reduced }) => {
    if (reduced) return
    gsap.from(q('.k-track'), { y: 24, opacity: 0, duration: 0.6, stagger: 0.08 })
  },
  { watch: () => load.data.value },
)

/** [{ category, groups: [{ section, topics[] }] }] in curriculum order */
const tracks = computed(() => {
  if (!load.data.value) return []
  const { categories, topics } = load.data.value
  return categories.map((category) => {
    const groups = []
    for (const topic of topics.filter((t) => t.category.slug === category.slug)) {
      const key = topic.section?.slug ?? '_'
      let group = groups.find((g) => g.key === key)
      if (!group) groups.push((group = { key, section: topic.section, topics: [] }))
      group.topics.push(topic)
    }
    return { category, groups }
  })
})
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <KEyebrow tone="muted">Prepare</KEyebrow>
    <h1 class="k-display mt-6 text-[clamp(2.75rem,7vw,5.5rem)]">
      Choose your<br /><span class="k-serif text-[1.05em]">track.</span>
    </h1>
    <p class="mt-6 max-w-xl text-lg text-muted">
      Three tracks, organised the way interviews test you. Pick a topic, work through it, watch the line fill up.
    </p>

    <KErrorState v-if="load.error.value" class="mt-12" :message="load.error.value.message" @retry="load.run" />

    <div v-else-if="!load.data.value" class="mt-16 grid grid-cols-1 gap-10 md:grid-cols-3">
      <KSkeleton v-for="n in 3" :key="n" :lines="5" height="1.5rem" />
    </div>

    <template v-else>
      <!-- Track overview -->
      <section ref="trackGrid" class="mt-16 grid grid-cols-1 gap-6 md:grid-cols-3" aria-label="Tracks">
        <!-- GSAP animates the wrapper; the card's own transform belongs to its CSS hover lift. -->
        <div v-for="({ category }, i) in tracks" :key="category.slug" class="k-track">
          <KTrackCard
            :to="{ name: 'practice', params: { category: category.slug } }"
            :index="i + 1"
            :glyph="category.glyph"
            :name="category.name"
            :description="category.description"
            :completed="category.completed_count"
            :total="category.question_count"
            :attempted="category.attempted_count"
          />
        </div>
      </section>

      <!-- Topics per track -->
      <section v-for="({ category, groups }, i) in tracks" :key="category.slug" v-reveal class="mt-24" :aria-labelledby="`topics-${category.slug}`">
        <header class="flex items-baseline justify-between gap-6 border-b border-rule pb-4">
          <KEyebrow :id="`topics-${category.slug}`" as="h2">{{ category.name }} topics</KEyebrow>
          <RouterLink :to="{ name: 'practice', params: { category: category.slug } }" class="k-eyebrow text-muted hover:text-accent-text">
            All questions →
          </RouterLink>
        </header>

        <div v-for="group in groups" :key="group.key" class="mt-8">
          <p v-if="group.section" class="k-eyebrow mb-4 text-muted">{{ group.section.name }}</p>
          <ul class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <li v-for="topic in group.topics" :key="topic.slug">
              <RouterLink
                :to="{ name: 'practice', params: { category: category.slug }, query: { topic: topic.slug } }"
                class="group flex h-full flex-col bg-surface p-5 transition-colors hover:bg-raised"
              >
                <span class="flex items-baseline justify-between gap-4">
                  <span class="text-lg font-medium tracking-tight group-hover:text-accent-text">{{ topic.name }}</span>
                  <span class="shrink-0 font-mono text-sm text-muted">{{ topic.completed_count }}/{{ topic.question_count }}</span>
                </span>
                <span class="mt-2 flex-1 text-sm text-muted">{{ topic.description }}</span>
                <span class="mt-5 block">
                  <KProgressBar :value="topic.completed_count" :max="topic.question_count" :label="`${topic.name} progress`" />
                </span>
              </RouterLink>
            </li>
          </ul>
        </div>
      </section>
    </template>
  </div>
</template>
