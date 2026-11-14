<script setup>
/**
 * Preparation hub ("Preparation Dashboard"): the three tracks with my
 * progress, then every topic grouped by track (and section for aptitude),
 * each linking into the practice library pre-filtered to that topic.
 */
import { computed, onMounted } from 'vue'

import KArrowLink from '@/components/ui/KArrowLink.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KProgressBar from '@/components/ui/KProgressBar.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useAsync } from '@/composables/useAsync'
import { catalogApi } from '@/services/catalog.api'
import { percent } from '@/utils/format'

const load = useAsync(async () => {
  const [categories, topics] = await Promise.all([catalogApi.categories(), catalogApi.topics()])
  return { categories, topics }
})
onMounted(load.run)

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
    <KEyebrow tone="muted" index="01">Prepare</KEyebrow>
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
      <section class="mt-16 grid grid-cols-1 gap-14 md:grid-cols-3 md:gap-10" aria-label="Tracks">
        <article v-for="({ category }, i) in tracks" :key="category.slug" class="flex flex-col border-t border-rule pt-8">
          <p class="font-mono text-sm">{{ String(i + 1).padStart(2, '0') }}</p>
          <p class="k-serif my-8 text-center text-[6rem] leading-none not-italic" aria-hidden="true">{{ category.glyph }}</p>
          <h2 class="text-2xl font-medium tracking-tight uppercase">{{ category.name }}</h2>
          <p class="mt-3 flex-1 text-muted">{{ category.description }}</p>
          <div class="mt-6 flex items-center gap-4">
            <KProgressBar :value="category.completed_count" :max="category.question_count" :label="`${category.name} progress`" />
            <span class="shrink-0 font-mono text-sm">{{ category.completed_count }}/{{ category.question_count }}</span>
          </div>
          <p class="mt-2 text-sm text-muted">
            {{ percent(category.question_count ? category.completed_count / category.question_count : 0) }} complete ·
            {{ category.attempted_count }} attempted
          </p>
          <div class="mt-8">
            <KArrowLink :to="{ name: 'practice', params: { category: category.slug } }">Practice</KArrowLink>
          </div>
        </article>
      </section>

      <!-- Topics per track -->
      <section v-for="({ category, groups }, i) in tracks" :key="category.slug" class="mt-24" :aria-labelledby="`topics-${category.slug}`">
        <header class="flex items-baseline justify-between gap-6 border-b border-rule pb-4">
          <KEyebrow :id="`topics-${category.slug}`" as="h2" :index="String(i + 2).padStart(2, '0')">{{ category.name }} topics</KEyebrow>
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
