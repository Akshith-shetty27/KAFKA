<script setup>
/**
 * Personal dashboard. Every number comes from the progress API:
 *   /progress/summary   → stats, streak, category progress
 *   /progress/plan      → today's plan + recommended topics
 *   /progress/activity  → last 7 days
 *   /progress/recent    → recently attempted questions
 * Each request loads independently with its own loading/error state.
 */
import { computed, onMounted } from 'vue'

import CategoryProgress from '@/components/dashboard/CategoryProgress.vue'
import DashboardPanel from '@/components/dashboard/DashboardPanel.vue'
import RecentQuestions from '@/components/dashboard/RecentQuestions.vue'
import RecommendedTopics from '@/components/dashboard/RecommendedTopics.vue'
import StatsRow from '@/components/dashboard/StatsRow.vue'
import TodayPlan from '@/components/dashboard/TodayPlan.vue'
import WeeklyActivity from '@/components/dashboard/WeeklyActivity.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KStreakBadge from '@/components/ui/KStreakBadge.vue'
import { useAsync } from '@/composables/useAsync'
import { progressApi } from '@/services/progress.api'
import { useAuthStore } from '@/stores/auth'
import { greeting, longDate } from '@/utils/format'

const auth = useAuthStore()

const summary = useAsync(() => progressApi.summary())
const plan = useAsync(() => progressApi.plan())
const activity = useAsync(() => progressApi.activity(7))
const recent = useAsync(() => progressApi.recent(6))

onMounted(() => {
  summary.run()
  plan.run()
  activity.run()
  recent.run()
})

const hello = greeting()
const isNewUser = computed(() => summary.data.value?.totals.attempted === 0)
const planProgress = computed(() =>
  plan.data.value ? `${plan.data.value.completed_today}/${plan.data.value.items.length}` : '',
)
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <!-- Welcome -->
    <section class="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <KEyebrow tone="muted">Dashboard<template v-if="plan.data.value"> / {{ longDate(plan.data.value.date) }}</template></KEyebrow>
        <h1 class="k-display mt-6 text-[clamp(2.75rem,7vw,5.5rem)]">
          {{ hello }},<br /><span class="k-serif text-[1.05em]">{{ auth.displayName }}.</span>
        </h1>
        <p class="mt-6 max-w-xl text-lg text-muted">
          <template v-if="isNewUser">Your first plan is ready below. Start small — one question today already counts.</template>
          <template v-else-if="plan.data.value">
            {{ plan.data.value.completed_today }} of {{ plan.data.value.items.length }} planned questions done today.
          </template>
        </p>
      </div>
      <KStreakBadge v-if="summary.data.value" :days="summary.data.value.streak.current" class="self-start lg:self-end" />
    </section>

    <!-- Stats -->
    <section class="mt-14 lg:mt-20" aria-label="Your numbers">
      <KErrorState v-if="summary.error.value" :message="summary.error.value.message" @retry="summary.run" />
      <div v-else-if="!summary.data.value" class="grid grid-cols-2 gap-6 lg:grid-cols-4">
        <KSkeleton v-for="n in 4" :key="n" :lines="2" height="2.5rem" />
      </div>
      <StatsRow v-else :summary="summary.data.value" />
    </section>

    <!-- Plan + week -->
    <div class="mt-20 grid grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
      <DashboardPanel
        class="lg:col-span-5"
        title="Today's plan"
        :loading="!plan.data.value && !plan.error.value"
        :error="plan.error.value"
        @retry="plan.run"
      >
        <template #aside><span class="k-eyebrow text-muted">{{ planProgress }}</span></template>
        <TodayPlan v-if="plan.data.value" :plan="plan.data.value" />
      </DashboardPanel>

      <DashboardPanel
        class="lg:col-span-6 lg:col-start-7"
        title="This week"
        :loading="!activity.data.value && !activity.error.value"
        :error="activity.error.value"
        @retry="activity.run"
      >
        <WeeklyActivity v-if="activity.data.value" :series="activity.data.value.series" />
      </DashboardPanel>
    </div>

    <!-- Categories + recommendations -->
    <div class="mt-20 grid grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
      <DashboardPanel
        class="lg:col-span-7"
        title="Progress by track"
        :loading="!summary.data.value && !summary.error.value"
        :error="summary.error.value"
        @retry="summary.run"
      >
        <CategoryProgress v-if="summary.data.value" :categories="summary.data.value.categories" />
      </DashboardPanel>

      <DashboardPanel
        class="lg:col-span-5"
        title="Recommended next"
        :loading="!plan.data.value && !plan.error.value"
        :error="plan.error.value"
        @retry="plan.run"
      >
        <RecommendedTopics v-if="plan.data.value" :topics="plan.data.value.recommended_topics" />
      </DashboardPanel>
    </div>

    <!-- Recent -->
    <DashboardPanel
      class="mt-20"
      title="Recently attempted"
      :loading="!recent.data.value && !recent.error.value"
      :error="recent.error.value"
      @retry="recent.run"
    >
      <RecentQuestions v-if="recent.data.value" :records="recent.data.value" />
    </DashboardPanel>
  </div>
</template>
