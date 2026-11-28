<script setup>
/**
 * Practice library for one track: /practice/coding, /practice/aptitude,
 * /practice/core-cs. Every filter lives in the URL query (?topic=&difficulty=
 * &status=&pattern=&q=&page=), so filtered views are linkable, survive a
 * refresh and work with the back button.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import QuestionTable from '@/components/catalog/QuestionTable.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KIcon from '@/components/ui/KIcon.vue'
import KPagination from '@/components/ui/KPagination.vue'
import KSelect from '@/components/ui/KSelect.vue'
import KProgressRing from '@/components/ui/KProgressRing.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useAsync } from '@/composables/useAsync'
import { catalogApi } from '@/services/catalog.api'

const PAGE_SIZE = 20
const route = useRoute()
const router = useRouter()

const category = computed(() => route.params.category)
const filters = computed(() => ({
  topic: route.query.topic ?? '',
  difficulty: route.query.difficulty ?? '',
  status: route.query.status ?? '',
  pattern: route.query.pattern ?? '',
  q: route.query.q ?? '',
  page: Number(route.query.page) || 1,
}))

/**
 * Change some filters; any change other than paging returns to page 1.
 * Clicked filters create a history entry (Back undoes them); typing in the
 * search box replaces the entry so every keystroke isn't a Back step.
 */
function setFilters(patch, { replace = false } = {}) {
  const next = { ...filters.value, ...patch }
  if (!('page' in patch)) next.page = 1
  const query = Object.fromEntries(Object.entries(next).filter(([k, v]) => v !== '' && !(k === 'page' && v === 1)))
  router[replace ? 'replace' : 'push']({ query })
}

// --- track meta (categories, topics, patterns) ------------------------------------
// A failed pattern list only empties the pattern filter, so it has no error UI.
const categories = useAsync(() => catalogApi.categories())
const topics = useAsync((slug) => catalogApi.topics(slug))
const patterns = useAsync(() => catalogApi.patterns())
categories.run()

const current = computed(() => categories.data.value?.find((c) => c.slug === category.value) ?? null)
const unknownTrack = computed(() => categories.data.value && !current.value)
const isCoding = computed(() => category.value === 'coding')

watch(
  category,
  (slug) => {
    topics.run(slug)
    if (slug === 'coding' && !patterns.data.value) patterns.run()
  },
  { immediate: true },
)

const topicGroups = computed(() => {
  const groups = []
  for (const topic of topics.data.value ?? []) {
    const key = topic.section?.slug ?? '_'
    let group = groups.find((g) => g.key === key)
    if (!group) groups.push((group = { key, section: topic.section, topics: [] }))
    group.topics.push(topic)
  }
  return groups
})
const topicOptions = computed(() => [
  { value: '', label: 'All topics' },
  ...(topics.data.value ?? []).map((t) => ({ value: t.slug, label: t.name })),
])
const activeTopic = computed(() => topics.data.value?.find((t) => t.slug === filters.value.topic) ?? null)

// --- questions ------------------------------------------------------------------------
const questions = useAsync(() =>
  catalogApi.questions({
    category: category.value,
    topic: filters.value.topic,
    difficulty: filters.value.difficulty,
    status: filters.value.status,
    pattern: isCoding.value ? filters.value.pattern : '',
    search: filters.value.q,
    page: filters.value.page,
    page_size: PAGE_SIZE,
  }),
)
watch([category, filters], () => questions.run(), { immediate: true, deep: true })

// A page past the end (e.g. a stale link after filtering) returns 404 → go back to page 1.
watch(
  () => questions.error.value,
  (err) => {
    if (err?.status === 404 && filters.value.page > 1) setFilters({ page: 1 }, { replace: true })
  },
)

// --- search (debounced) ------------------------------------------------------------------
const searchText = ref(filters.value.q)
let searchTimer
watch(searchText, (text) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    if (text.trim() !== filters.value.q) setFilters({ q: text.trim() }, { replace: true })
  }, 300)
})
watch(
  () => filters.value.q,
  (q) => {
    if (q !== searchText.value.trim()) searchText.value = q
  },
)

const hasFilters = computed(() =>
  ['topic', 'difficulty', 'status', 'pattern', 'q'].some((k) => filters.value[k] !== ''),
)
function clearFilters() {
  searchText.value = ''
  router.replace({ query: {} })
}

const difficulties = [
  { value: '', label: 'All' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]
const statuses = [
  { value: '', label: 'Any status' },
  { value: 'not_started', label: 'Not started' },
  { value: 'attempted', label: 'Attempted' },
  { value: 'completed', label: 'Completed' },
]
const patternOptions = computed(() => [
  { value: '', label: 'All patterns' },
  ...(patterns.data.value ?? []).map((p) => ({ value: p.slug, label: p.name })),
])
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <!-- Track tabs -->
    <nav class="flex gap-8 overflow-x-auto border-b border-rule-soft" aria-label="Tracks">
      <RouterLink
        v-for="c in categories.data.value ?? []"
        :key="c.slug"
        :to="{ name: 'practice', params: { category: c.slug } }"
        class="k-label -mb-px shrink-0 border-b-2 pb-4 transition-colors"
        :class="c.slug === category ? 'border-accent text-fg' : 'border-transparent text-muted hover:text-fg'"
        :aria-current="c.slug === category ? 'page' : undefined"
      >
        {{ c.name }}
      </RouterLink>
    </nav>

    <KErrorState v-if="categories.error.value" class="mt-10" :message="categories.error.value.message" @retry="categories.run" />
    <KEmptyState v-else-if="unknownTrack" class="mt-10" title="Unknown track">
      There's no track called “{{ category }}”. Pick one of the tabs above.
    </KEmptyState>

    <template v-else>
      <!-- Heading -->
      <header class="mt-10 flex items-end justify-between gap-8 lg:mt-14">
        <div>
          <KEyebrow tone="muted">Practice · {{ current?.name ?? '…' }}</KEyebrow>
          <h1 class="k-display mt-5 text-[clamp(2.5rem,6vw,4.75rem)]">
            {{ activeTopic ? activeTopic.name : current?.name ?? '' }}<span class="text-accent">.</span>
          </h1>
          <p class="mt-4 max-w-2xl text-lg text-muted">{{ activeTopic?.description || current?.description }}</p>
        </div>
        <span v-if="current" class="k-serif hidden text-8xl leading-none not-italic md:block" aria-hidden="true">{{ current.glyph }}</span>
      </header>

      <div class="mt-12 grid grid-cols-1 gap-10 lg:grid-cols-12">
        <!-- Topic list (desktop) -->
        <aside class="hidden lg:col-span-3 lg:block" aria-label="Topics">
          <KErrorState v-if="topics.error.value" :message="topics.error.value.message" @retry="topics.run(category)" />
          <KSkeleton v-else-if="!topics.data.value" :lines="8" />
          <nav v-else class="sticky top-28 flex flex-col gap-6">
            <button
              type="button"
              class="flex items-baseline justify-between text-left text-sm transition-colors"
              :class="!filters.topic ? 'font-medium text-fg' : 'text-muted hover:text-fg'"
              @click="setFilters({ topic: '' })"
            >
              <span>All topics</span>
              <span class="font-mono text-xs">{{ current?.question_count }}</span>
            </button>
            <div v-for="group in topicGroups" :key="group.key">
              <p v-if="group.section" class="k-eyebrow mb-3 text-muted">{{ group.section.name }}</p>
              <ul class="flex flex-col gap-2.5 border-l border-rule-soft">
                <li v-for="t in group.topics" :key="t.slug">
                  <button
                    type="button"
                    class="-ml-px flex w-full items-baseline justify-between gap-3 border-l-2 pl-4 text-left text-sm transition-colors"
                    :class="filters.topic === t.slug ? 'border-accent font-medium text-fg' : 'border-transparent text-muted hover:text-fg'"
                    :aria-current="filters.topic === t.slug ? 'true' : undefined"
                    @click="setFilters({ topic: t.slug })"
                  >
                    <span>{{ t.name }}</span>
                    <span class="flex shrink-0 items-center gap-2 font-mono text-xs">
                      {{ t.completed_count }}/{{ t.question_count }}
                      <KProgressRing :value="t.completed_count" :max="t.question_count" :label="`${t.name} progress`" :size="14" :stroke="2" decorative />
                    </span>
                  </button>
                </li>
              </ul>
            </div>
          </nav>
        </aside>

        <section class="lg:col-span-9" aria-label="Questions">
          <!-- Filters -->
          <div class="flex flex-col gap-5 border-b border-rule-soft pb-6">
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:hidden">
              <KSelect :model-value="filters.topic" label="Topic" :options="topicOptions" @update:model-value="setFilters({ topic: $event })" />
              <KSelect :model-value="filters.status" label="Status" :options="statuses" @update:model-value="setFilters({ status: $event })" />
            </div>

            <div class="flex flex-wrap items-center gap-x-6 gap-y-4">
              <label class="relative min-w-[14rem] flex-1">
                <span class="sr-only">Search questions</span>
                <KIcon name="search" :size="16" class="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-muted" />
                <input
                  v-model="searchText"
                  type="search"
                  placeholder="Search by title or topic"
                  class="h-11 w-full rounded-[2px] border border-rule-soft bg-transparent pr-3 pl-10 text-[15px] outline-none placeholder:text-muted/70 hover:border-muted focus:border-accent"
                />
              </label>

              <div class="flex" role="group" aria-label="Difficulty">
                <button
                  v-for="d in difficulties"
                  :key="d.value"
                  type="button"
                  class="k-eyebrow -ml-px h-11 border px-3.5 tracking-[0.15em] transition-colors first:ml-0"
                  :class="filters.difficulty === d.value ? 'relative z-10 border-accent bg-accent text-on-accent' : 'border-rule-soft text-muted hover:text-fg'"
                  :aria-pressed="filters.difficulty === d.value"
                  @click="setFilters({ difficulty: d.value })"
                >
                  {{ d.label }}
                </button>
              </div>

              <div class="hidden w-44 lg:block">
                <label class="sr-only" for="status-filter">Status</label>
                <select
                  id="status-filter"
                  :value="filters.status"
                  class="h-11 w-full rounded-[2px] border border-rule-soft bg-canvas px-3 text-sm outline-none hover:border-muted focus:border-accent"
                  @change="setFilters({ status: $event.target.value })"
                >
                  <option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>

              <div v-if="isCoding" class="w-48">
                <label class="sr-only" for="pattern-filter">Pattern</label>
                <select
                  id="pattern-filter"
                  :value="filters.pattern"
                  class="h-11 w-full rounded-[2px] border border-rule-soft bg-canvas px-3 text-sm outline-none hover:border-muted focus:border-accent"
                  @change="setFilters({ pattern: $event.target.value })"
                >
                  <option v-for="p in patternOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
                </select>
              </div>

              <button v-if="hasFilters" type="button" class="k-eyebrow inline-flex items-center gap-2 text-muted hover:text-fg" @click="clearFilters">
                <KIcon name="x" :size="14" /> Clear
              </button>
            </div>
          </div>

          <!-- Results -->
          <div class="mt-6" aria-live="polite" :aria-busy="questions.loading.value">
            <KErrorState v-if="questions.error.value && questions.error.value.status !== 404" :message="questions.error.value.message" @retry="questions.run" />
            <KSkeleton v-else-if="!questions.data.value" :lines="8" height="2.75rem" />
            <template v-else>
              <KEmptyState v-if="questions.data.value.count === 0" title="No questions match">
                Try another difficulty or status, or
                <button type="button" class="underline underline-offset-4 hover:text-fg" @click="clearFilters">clear all filters</button>.
              </KEmptyState>
              <template v-else>
                <!-- Keyed by the result set, so rows rise in again whenever filters change the list. -->
                <QuestionTable
                  :key="questions.data.value.results.map((q) => q.slug).join()"
                  :questions="questions.data.value.results"
                  :show-topic="!filters.topic"
                  :show-patterns="isCoding"
                  :show-type="category === 'core-cs'"
                  :class="questions.loading.value ? 'opacity-60 transition-opacity' : ''"
                />
                <KPagination
                  class="mt-8"
                  :page="filters.page"
                  :count="questions.data.value.count"
                  :page-size="PAGE_SIZE"
                  @update:page="setFilters({ page: $event })"
                />
              </template>
            </template>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
