<script setup>
/**
 * Personal dashboard. Every number comes from the API — nothing is invented:
 *   /progress/summary   → stats, streak, track order and glyphs
 *   /progress/plan      → today's objective, plan and recommended topics
 *   /progress/activity  → the 90-day heatmap and this week's numbers
 *   /progress/recent    → recently attempted questions
 *   /topics/            → per-topic progress, summed into the track cards
 * Each request loads independently with its own loading/error state.
 */
import { onMounted } from 'vue'

import ActivityPanel from '@/components/dashboard/ActivityPanel.vue'
import DashboardPanel from '@/components/dashboard/DashboardPanel.vue'
import RecentQuestions from '@/components/dashboard/RecentQuestions.vue'
import RecommendedTopics from '@/components/dashboard/RecommendedTopics.vue'
import StatsRow from '@/components/dashboard/StatsRow.vue'
import TodayPlan from '@/components/dashboard/TodayPlan.vue'
import TrackOverview from '@/components/dashboard/TrackOverview.vue'
import WelcomeHero from '@/components/dashboard/WelcomeHero.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { useAsync } from '@/composables/useAsync'
import { catalogApi } from '@/services/catalog.api'
import { progressApi } from '@/services/progress.api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const summary = useAsync(() => progressApi.summary())
const plan = useAsync(() => progressApi.plan())
const activity = useAsync(() => progressApi.activity(90))
const recent = useAsync(() => progressApi.recent(6))
const topics = useAsync(() => catalogApi.topics())

onMounted(() => {
  summary.run()
  plan.run()
  activity.run()
  recent.run()
  topics.run()
})
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <WelcomeHero :name="auth.displayName" :plan="plan.data.value" :summary="summary.data.value" />

    <!-- Stats -->
    <section class="mt-16 lg:mt-20" aria-label="Your numbers">
      <KErrorState v-if="summary.error.value" :message="summary.error.value.message" @retry="summary.run" />
      <div v-else-if="!summary.data.value" class="grid grid-cols-2 gap-6 lg:grid-cols-4">
        <KSkeleton v-for="n in 4" :key="n" :lines="2" height="2.5rem" />
      </div>
      <StatsRow v-else :summary="summary.data.value" />
    </section>

    <!-- Tracks -->
    <DashboardPanel
      v-reveal
      class="mt-20"
      title="Your tracks"
      :loading="!(summary.data.value && topics.data.value) && !summary.error.value && !topics.error.value"
      :error="summary.error.value ?? topics.error.value"
      @retry="() => (summary.error.value ? summary.run() : topics.run())"
    >
      <template #aside>
        <RouterLink :to="{ name: 'prepare' }" class="k-eyebrow text-muted hover:text-accent-text">All topics →</RouterLink>
      </template>
      <TrackOverview v-if="summary.data.value && topics.data.value" :categories="summary.data.value.categories" :topics="topics.data.value" />
    </DashboardPanel>

    <!-- Plan + activity -->
    <div class="mt-20 grid grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
      <DashboardPanel
        v-reveal
        class="lg:col-span-5"
        title="Today's plan"
        :loading="!plan.data.value && !plan.error.value"
        :error="plan.error.value"
        @retry="plan.run"
      >
        <template v-if="plan.data.value" #aside>
          <span class="k-eyebrow text-muted">{{ plan.data.value.completed_today }}/{{ plan.data.value.items.length }}</span>
        </template>
        <TodayPlan v-if="plan.data.value" :plan="plan.data.value" />
      </DashboardPanel>

      <DashboardPanel
        v-reveal="{ delay: 0.08 }"
        class="lg:col-span-6 lg:col-start-7"
        title="Activity"
        :loading="!activity.data.value && !activity.error.value"
        :error="activity.error.value"
        @retry="activity.run"
      >
        <template #aside><span class="k-eyebrow text-muted">Last 90 days</span></template>
        <ActivityPanel v-if="activity.data.value" :series="activity.data.value.series" />
      </DashboardPanel>
    </div>

    <!-- Recommendations + recent -->
    <div class="mt-20 grid grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
      <DashboardPanel
        v-reveal
        class="lg:col-span-5"
        title="Recommended next"
        :loading="!plan.data.value && !plan.error.value"
        :error="plan.error.value"
        @retry="plan.run"
      >
        <RecommendedTopics v-if="plan.data.value" :topics="plan.data.value.recommended_topics" />
      </DashboardPanel>

      <DashboardPanel
        v-reveal="{ delay: 0.08 }"
        class="lg:col-span-6 lg:col-start-7"
        title="Recently attempted"
        :loading="!recent.data.value && !recent.error.value"
        :error="recent.error.value"
        @retry="recent.run"
      >
        <RecentQuestions v-if="recent.data.value" :records="recent.data.value" />
      </DashboardPanel>
    </div>
  </div>
</template>
