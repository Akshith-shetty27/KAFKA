<script setup>
/**
 * Dashboard opener: greeting, date, and today's objective — the daily goal as
 * a ring plus a direct link to the next question in today's plan. All values
 * come from /progress/plan and /progress/summary.
 */
import { computed, ref } from 'vue'

import KIcon from '@/components/ui/KIcon.vue'
import KProgressRing from '@/components/ui/KProgressRing.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import KStreakBadge from '@/components/ui/KStreakBadge.vue'
import { useMotion } from '@/motion'
import { greeting, longDate } from '@/utils/format'

const props = defineProps({
  name: { type: String, required: true },
  plan: { type: Object, default: null }, // /progress/plan
  summary: { type: Object, default: null }, // /progress/summary
})

const hello = greeting()
const isNewUser = computed(() => props.summary?.totals.attempted === 0)
const done = computed(() => props.plan?.completed_today ?? 0)
const goal = computed(() => props.plan?.items.length ?? 0)
const next = computed(() => props.plan?.items.find((i) => !i.done)?.question ?? null)
const remaining = computed(() => Math.max(0, goal.value - done.value))

// The greeting's two lines rise in once, on first view.
const root = ref(null)
useMotion(root, ({ q, gsap, reduced }) => {
  if (reduced) return
  gsap.from(q('.k-hero-line'), { yPercent: 60, opacity: 0, duration: 0.8, stagger: 0.09 })
  gsap.from(q('.k-hero-fade'), { y: 12, opacity: 0, duration: 0.7, delay: 0.25, stagger: 0.08 })
})
</script>

<template>
  <section ref="root" class="grid grid-cols-1 gap-10 lg:grid-cols-12 lg:items-end" aria-labelledby="dash-greeting">
    <div class="lg:col-span-7">
      <p class="k-eyebrow k-hero-fade text-muted">Dashboard<template v-if="plan"> / {{ longDate(plan.date) }}</template></p>
      <h1 id="dash-greeting" class="k-display mt-6 text-[clamp(2.75rem,7vw,5.5rem)]">
        <span class="block overflow-hidden pb-[0.06em]"><span class="k-hero-line block">{{ hello }},</span></span>
        <span class="block overflow-hidden pb-[0.12em]"><span class="k-hero-line k-serif block text-[1.05em]">{{ name }}.</span></span>
      </h1>
      <p class="k-hero-fade mt-6 max-w-xl text-lg text-muted">
        <template v-if="isNewUser">Your first plan is ready. Start small — one question today already counts.</template>
        <template v-else-if="plan && remaining === 0">Today's goal is done. Anything more is a bonus.</template>
        <template v-else-if="plan">{{ remaining }} question{{ remaining === 1 ? '' : 's' }} left in today's plan.</template>
        <template v-else>&nbsp;</template>
      </p>
    </div>

    <!-- Today's objective -->
    <div class="k-hero-fade lg:col-span-5">
      <div class="border border-rule-soft bg-surface p-6 shadow-elevated sm:p-7">
        <div class="flex items-center justify-between gap-4">
          <p class="k-eyebrow text-muted">Today's objective</p>
          <KStreakBadge v-if="summary" :days="summary.streak.current" compact />
        </div>
        <KSkeleton v-if="!plan" class="mt-6" :lines="3" height="1.25rem" />
        <div v-else class="mt-6 flex items-center gap-6">
          <KProgressRing :value="done" :max="goal || 1" label="Today's goal progress" :size="112" :stroke="6">
            <span class="text-center">
              <span class="k-serif block text-4xl leading-none">{{ done }}<span class="text-xl text-muted">/{{ goal }}</span></span>
              <span class="k-eyebrow mt-1 block text-[9px] text-muted">done</span>
            </span>
          </KProgressRing>
          <div class="min-w-0 flex-1">
            <template v-if="next">
              <p class="text-sm text-muted">Next up</p>
              <p class="mt-1 truncate font-medium">{{ next.title }}</p>
              <p class="mt-0.5 truncate text-sm text-muted">{{ next.category.name }} · {{ next.topic.name }}</p>
              <RouterLink
                :to="{ name: 'question', params: { slug: next.slug } }"
                class="k-label mt-4 inline-flex items-center gap-2 bg-accent px-4 py-2.5 text-xs text-on-accent transition-[filter] hover:brightness-95"
              >
                Continue <KIcon name="arrow-right" :size="14" />
              </RouterLink>
            </template>
            <template v-else>
              <p class="font-medium">Goal reached.</p>
              <p class="mt-1 text-sm text-muted">Keep going with a recommended topic below, or rest — the streak is safe.</p>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
