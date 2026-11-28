<script setup>
/**
 * Progress analytics. Data:
 *   /progress/summary   → headline numbers, streak, per-track progress
 *   /progress/activity  → 365-day series for the heatmap
 *   /progress/insights  → per-topic completion + first-try accuracy,
 *                         difficulty breakdown, focus areas
 */
import { computed, onMounted, ref } from 'vue'

import DashboardPanel from '@/components/dashboard/DashboardPanel.vue'
import StatsRow from '@/components/dashboard/StatsRow.vue'
import KArrowLink from '@/components/ui/KArrowLink.vue'
import KCountUp from '@/components/ui/KCountUp.vue'
import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KHeatmap from '@/components/ui/KHeatmap.vue'
import KProgressBar from '@/components/ui/KProgressBar.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useAsync } from '@/composables/useAsync'
import { progressApi } from '@/services/progress.api'
import { longDate, percent } from '@/utils/format'

const summary = useAsync(() => progressApi.summary())
const activity = useAsync(() => progressApi.activity(365))
const insights = useAsync(() => progressApi.insights())
onMounted(() => {
  summary.run()
  activity.run()
  insights.run()
})

const isNewUser = computed(() => summary.data.value?.totals.attempted === 0)

const activityStats = computed(() => {
  const series = activity.data.value?.series ?? []
  const active = series.filter((d) => d.questions > 0)
  const best = active.reduce((b, d) => (d.questions > (b?.questions ?? 0) ? d : b), null)
  return {
    activeDays: active.length,
    questions: series.reduce((n, d) => n + d.questions, 0),
    aiMessages: series.reduce((n, d) => n + d.ai_messages, 0),
    best,
  }
})

// Topic table, one track at a time.
const track = ref('coding')
const tracks = computed(() => summary.data.value?.categories ?? [])
const trackTopics = computed(() => (insights.data.value?.topics ?? []).filter((t) => t.category.slug === track.value))

// Tabs follow the ARIA tabs pattern: one tab stop, arrow keys / Home / End move between tracks.
const tabRefs = ref([])
function onTabKey(event, index) {
  const n = tracks.value.length
  const next = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: n - 1 }[event.key]
  if (next === undefined) return
  event.preventDefault()
  const i = (next + n) % n
  track.value = tracks.value[i].slug
  tabRefs.value[i]?.focus()
}

function focusReason(area) {
  const t = area.topic
  if (area.reason === 'low_accuracy') {
    return `${t.first_attempt_correct} of ${t.first_attempt_total} right on the first try (${percent(t.first_attempt_accuracy)}). Review the explanations, then retry.`
  }
  return `Started, ${t.completed_count} of ${t.question_count} done. Finish it while it's fresh.`
}
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <KEyebrow tone="muted" index="01">Progress</KEyebrow>
    <h1 class="k-display mt-6 text-[clamp(2.75rem,7vw,5.5rem)]">
      Your<br /><span class="k-serif text-[1.05em]">trajectory.</span>
    </h1>
    <p class="mt-6 max-w-xl text-lg text-muted">Every question you open, answer or finish — and where to look next.</p>

    <!-- Headline numbers -->
    <section class="mt-14" aria-label="Your numbers">
      <KErrorState v-if="summary.error.value" :message="summary.error.value.message" @retry="summary.run" />
      <div v-else-if="!summary.data.value" class="grid grid-cols-2 gap-6 lg:grid-cols-4">
        <KSkeleton v-for="n in 4" :key="n" :lines="2" height="2.5rem" />
      </div>
      <StatsRow v-else :summary="summary.data.value" />
    </section>

    <KEmptyState v-if="isNewUser" class="mt-16" title="Nothing to chart yet" glyph="◎">
      Your graphs fill in as you practise.
      <RouterLink :to="{ name: 'prepare' }" class="ml-1 underline underline-offset-4 hover:text-fg">Pick a topic to start</RouterLink>.
    </KEmptyState>

    <!-- Activity -->
    <DashboardPanel
      v-reveal
      class="mt-20"
      title="Last 12 months"
      index="02"
      :loading="!activity.data.value && !activity.error.value"
      :error="activity.error.value"
      @retry="activity.run"
    >
      <template v-if="activity.data.value">
        <KHeatmap :series="activity.data.value.series" interactive label="Questions practised per day, last 12 months" />
        <dl class="mt-8 grid grid-cols-2 gap-6 border-t border-rule-soft pt-6 sm:grid-cols-4">
          <div>
            <dt class="k-eyebrow text-muted">Active days</dt>
            <dd class="k-serif mt-2 text-4xl"><KCountUp :value="activityStats.activeDays" /></dd>
          </div>
          <div>
            <dt class="k-eyebrow text-muted">Questions</dt>
            <dd class="k-serif mt-2 text-4xl"><KCountUp :value="activityStats.questions" /></dd>
          </div>
          <div>
            <dt class="k-eyebrow text-muted">Ask Kafka messages</dt>
            <dd class="k-serif mt-2 text-4xl"><KCountUp :value="activityStats.aiMessages" /></dd>
          </div>
          <div>
            <dt class="k-eyebrow text-muted">Busiest day</dt>
            <dd class="mt-2 text-sm">
              <template v-if="activityStats.best">
                <span class="k-serif text-4xl">{{ activityStats.best.questions }}</span>
                <span class="mt-1 block text-muted">{{ longDate(activityStats.best.date) }}</span>
              </template>
              <span v-else class="k-serif text-4xl">—</span>
            </dd>
          </div>
        </dl>
      </template>
    </DashboardPanel>

    <!-- Tracks + difficulty -->
    <div class="mt-20 grid grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
      <DashboardPanel
        v-reveal
        class="lg:col-span-7"
        title="By track"
        index="03"
        :loading="!summary.data.value && !summary.error.value"
        :error="summary.error.value"
        @retry="summary.run"
      >
        <ul v-if="summary.data.value" class="flex flex-col">
          <li v-for="(c, i) in tracks" :key="c.slug" class="grid grid-cols-[3.5rem_1fr] gap-5 py-5" :class="i ? 'border-t border-rule-soft' : ''">
            <span class="k-serif text-center text-4xl leading-none not-italic" aria-hidden="true">{{ c.glyph }}</span>
            <div class="min-w-0">
              <div class="flex items-baseline justify-between gap-4">
                <h3 class="font-medium tracking-tight uppercase">{{ c.name }}</h3>
                <span class="font-mono text-sm">{{ percent(c.question_count ? c.completed_count / c.question_count : 0) }}</span>
              </div>
              <div class="mt-3">
                <KProgressBar :value="c.completed_count" :max="c.question_count" :label="`${c.name} completion`" />
              </div>
              <p class="mt-2.5 text-sm text-muted">
                {{ c.completed_count }}/{{ c.question_count }} completed · {{ c.attempted_count }} attempted
                <template v-if="c.answers_total">· {{ percent(c.answers_correct / c.answers_total) }} of MCQ answers correct</template>
              </p>
            </div>
          </li>
        </ul>
      </DashboardPanel>

      <DashboardPanel
        v-reveal="{ delay: 0.08 }"
        class="lg:col-span-5"
        title="By difficulty"
        index="04"
        :loading="!insights.data.value && !insights.error.value"
        :error="insights.error.value"
        @retry="insights.run"
      >
        <ul v-if="insights.data.value" class="flex flex-col gap-6">
          <li v-for="d in insights.data.value.difficulty" :key="d.difficulty">
            <div class="flex items-baseline justify-between">
              <span class="k-eyebrow inline-flex items-center gap-2">
                <span
                  class="size-2 rounded-full"
                  :class="{ 'bg-accent': d.difficulty === 'easy', 'bg-warning': d.difficulty === 'medium', 'bg-danger': d.difficulty === 'hard' }"
                  aria-hidden="true"
                />
                {{ d.difficulty }}
              </span>
              <span class="font-mono text-sm text-muted">{{ d.completed_count }}/{{ d.question_count }}</span>
            </div>
            <div class="mt-3">
              <KProgressBar :value="d.completed_count" :max="d.question_count" :label="`${d.difficulty} questions completed`" />
            </div>
          </li>
        </ul>
      </DashboardPanel>
    </div>

    <!-- Focus areas -->
    <DashboardPanel
      v-reveal
      class="mt-20"
      title="Focus areas"
      index="05"
      :loading="!insights.data.value && !insights.error.value"
      :error="insights.error.value"
      @retry="insights.run"
    >
      <template v-if="insights.data.value">
        <ul v-if="insights.data.value.focus_areas.length" class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <li v-for="area in insights.data.value.focus_areas" :key="area.topic.slug" class="k-lift flex flex-col border border-rule-soft bg-surface p-5 hover:border-rule">
            <p class="k-eyebrow" :class="area.reason === 'low_accuracy' ? 'text-danger' : 'text-warning'">
              {{ area.reason === 'low_accuracy' ? 'Accuracy' : 'Unfinished' }} · {{ area.topic.category.name }}
            </p>
            <h3 class="mt-3 text-xl font-medium tracking-tight">{{ area.topic.name }}</h3>
            <p class="mt-2 flex-1 text-sm text-muted">{{ focusReason(area) }}</p>
            <div class="mt-5">
              <KArrowLink :to="{ name: 'practice', params: { category: area.topic.category.slug }, query: { topic: area.topic.slug } }">
                Practise
              </KArrowLink>
            </div>
          </li>
        </ul>
        <p v-else class="text-muted">
          Nothing needs attention right now. Focus areas appear when a topic's first-try accuracy dips or a topic is left
          half-done.
        </p>
      </template>
    </DashboardPanel>

    <!-- Topics -->
    <DashboardPanel
      v-reveal
      class="mt-20"
      title="Every topic"
      index="06"
      :loading="!insights.data.value && !insights.error.value"
      :error="insights.error.value"
      @retry="insights.run"
    >
      <template #aside>
        <div class="flex gap-5" role="tablist" aria-label="Track">
          <button
            v-for="(c, i) in tracks"
            :id="`topics-tab-${c.slug}`"
            :key="c.slug"
            :ref="(el) => (tabRefs[i] = el)"
            type="button"
            role="tab"
            :aria-selected="track === c.slug"
            aria-controls="topics-panel"
            :tabindex="track === c.slug ? 0 : -1"
            class="k-eyebrow -mb-px border-b pb-1 transition-colors"
            :class="track === c.slug ? 'border-accent text-fg' : 'border-transparent text-muted hover:text-fg'"
            @click="track = c.slug"
            @keydown="onTabKey($event, i)"
          >
            {{ c.name }}
          </button>
        </div>
      </template>
      <div
        v-if="insights.data.value"
        id="topics-panel"
        class="overflow-x-auto"
        role="tabpanel"
        :aria-labelledby="`topics-tab-${track}`"
      >
        <table class="w-full min-w-[34rem] text-sm">
          <thead>
            <tr class="k-eyebrow text-left text-muted">
              <th scope="col" class="pb-3 font-normal">Topic</th>
              <th scope="col" class="w-2/5 pb-3 font-normal">Completion</th>
              <th scope="col" class="pb-3 text-right font-normal">Done</th>
              <th scope="col" class="pb-3 text-right font-normal">First-try</th>
            </tr>
          </thead>
          <!-- Keyed by track, so rows rise in again when switching tabs. -->
          <tbody :key="track">
            <tr v-for="(t, i) in trackTopics" :key="t.slug" class="k-rise-quick border-t border-rule-soft" :style="{ '--i': Math.min(i, 12) }">
              <td class="py-3.5 pr-4">
                <RouterLink
                  :to="{ name: 'practice', params: { category: t.category.slug }, query: { topic: t.slug } }"
                  class="font-medium hover:text-accent-text"
                >
                  {{ t.name }}
                </RouterLink>
                <span v-if="t.section" class="block text-xs text-muted">{{ t.section }}</span>
              </td>
              <td class="py-3.5 pr-4">
                <KProgressBar :value="t.completed_count" :max="t.question_count" :label="`${t.name} completion`" />
              </td>
              <td class="py-3.5 text-right font-mono">{{ t.completed_count }}/{{ t.question_count }}</td>
              <td class="py-3.5 text-right font-mono">{{ t.first_attempt_total ? percent(t.first_attempt_accuracy) : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DashboardPanel>
  </div>
</template>
