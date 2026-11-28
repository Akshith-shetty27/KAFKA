<script setup>
/**
 * Public landing page, set in deep space (a two-layer starfield behind the
 * whole page): 001 hero with the question planet · 002 how it works ·
 * 003 the three tracks · "show up" closing section.
 * The hero's question count is real (catalog stats). The closing section's
 * numbers (07-day streak, weekly bars) are illustrative marketing visuals,
 * not user data — the dashboard shows the real thing.
 */
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'

import KArrowLink from '@/components/ui/KArrowLink.vue'
import KBarChart from '@/components/ui/KBarChart.vue'
import { loadScrollTrigger, useMotion } from '@/motion'
import { catalogApi } from '@/services/catalog.api'
import { useAuthStore } from '@/stores/auth'

// three.js + the scene live in their own chunk, requested only after first paint.
const HeroScene = defineAsyncComponent(() => import('@/components/landing/HeroScene.vue'))

const auth = useAuthStore()
const startTo = computed(() => (auth.isAuthenticated ? { name: 'dashboard' } : { name: 'register' }))

// --- hero scene: one point per real question, coloured by track ------------------------
const TRACK_COLORS = { coding: '#22dcc8', aptitude: '#7fd3e6', 'core-cs': '#9c988c' }
const stats = ref(null)
const showScene = ref(false)
const sceneFailed = ref(false)
const bands = computed(() =>
  (stats.value?.tracks ?? []).map((t) => ({ ...t, color: TRACK_COLORS[t.slug] ?? '#fffcf2' })),
)
onMounted(async () => {
  try {
    stats.value = await catalogApi.stats()
  } catch {
    return // no numbers → no scene; the panel's grid texture stays as designed
  }
  // After first paint, when the browser is idle — but at most 1.5 s later, since a
  // busy or throttled page might never report being idle.
  const reveal = () => (showScene.value = true)
  if (window.requestIdleCallback) window.requestIdleCallback(reveal, { timeout: 1500 })
  else setTimeout(reveal, 200)
})

// --- scroll storytelling (ScrollTrigger is loaded only on this page) ------------------
const page = ref(null)
const scrollTrigger = ref(null)
onMounted(async () => {
  scrollTrigger.value = await loadScrollTrigger()
})
useMotion(
  page,
  ({ q, gsap, reduced }) => {
    if (reduced) return
    for (const head of q('.k-story-head')) {
      gsap.from(head, { y: 48, opacity: 0, duration: 0.9, scrollTrigger: { trigger: head, start: 'top 85%' } })
    }
    gsap.from(q('.k-story-step'), {
      y: 32,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      scrollTrigger: { trigger: q('.k-story-steps')[0], start: 'top 80%' },
    })
    gsap.from(q('.k-story-track'), {
      y: 40,
      opacity: 0,
      duration: 0.8,
      stagger: 0.12,
      scrollTrigger: { trigger: q('.k-story-tracks')[0], start: 'top 80%' },
    })
    // Closing lines drift into alignment as the section scrolls into view.
    q('.k-story-line').forEach((line, i) => {
      gsap.fromTo(
        line,
        { xPercent: [-8, 8, -4][i] ?? 0 },
        { xPercent: 0, ease: 'none', scrollTrigger: { trigger: line, start: 'top bottom', end: 'center 55%', scrub: 0.6 } },
      )
    })
  },
  { watch: () => scrollTrigger.value },
)

const steps = [
  {
    n: '01',
    title: 'Pick a track',
    body: 'Coding, aptitude or core CS — questions organised by the patterns interviewers actually test.',
  },
  {
    n: '02',
    title: 'Get unstuck, not spoiled',
    body: 'Ask KAFKA reads the question you’re on and nudges you with hints before it ever shows a solution.',
  },
  {
    n: '03',
    title: 'Plan for the real job',
    body: 'Paste a job description and KAFKA builds a study plan for that exact role — then tracks it with you.',
  },
]

const tracks = [
  {
    n: '01',
    glyph: '{ }',
    title: 'Coding practice',
    body: 'Sharpen problem-solving through structured practice, organised by the patterns interviewers actually test.',
  },
  {
    n: '02',
    glyph: 'Σ',
    title: 'Aptitude training',
    body: 'Build speed and accuracy for placement assessments — quantitative, logical and verbal.',
  },
  {
    n: '03',
    glyph: '◎',
    title: 'Core CS prep',
    body: 'Revise DBMS, operating systems, networks, OOP and SQL for the technical theory round.',
  },
]

const week = [
  { label: 'M', value: 3 },
  { label: 'T', value: 5 },
  { label: 'W', value: 4 },
  { label: 'T', value: 7 },
  { label: 'F', value: 5 },
  { label: 'S', value: 7 },
  { label: 'S', value: 7 },
]
</script>

<template>
  <div ref="page" class="k-space">
  <div class="k-stars-far" aria-hidden="true" />
  <div class="k-stars-near" aria-hidden="true" />

  <!-- 001 · HERO: the question planet floats in the sky ------------------------ -->
  <div class="k-cosmos">
  <section class="k-container relative grid grid-cols-1 gap-14 pt-10 pb-20 lg:grid-cols-12 lg:gap-10 lg:pt-16 lg:pb-28">
    <div class="lg:col-span-7">
      <h1 class="k-display text-[clamp(3.4rem,10.5vw,8.25rem)]">
        <span class="k-rise block" style="--i: 1">Your next</span>
        <span class="k-serif k-rise block py-[0.04em] text-[1.06em] leading-[0.95]" style="--i: 2">big thing</span>
        <span class="k-rise block" style="--i: 3">starts</span>
        <span class="k-rise block" style="--i: 4">here.</span>
      </h1>
      <p class="k-rise mt-10 max-w-xl text-lg leading-relaxed sm:text-xl lg:mt-16" style="--i: 5">
        A smarter way to prepare for coding interviews, aptitude tests, and your next placement opportunity.
      </p>
      <div class="k-rise mt-10 flex flex-wrap items-center gap-x-12 gap-y-6" style="--i: 6">
        <KArrowLink :to="startTo">Start preparing</KArrowLink>
        <KArrowLink :to="{ hash: '#method' }" icon="chevron-right" :underline="false">Explore KAFKA</KArrowLink>
      </div>
    </div>

    <div class="lg:col-span-5">
      <div class="k-rise relative flex h-full min-h-[36rem] flex-col" style="--i: 3">
        <!-- The globe fills the space above the line, centred in it; the two never overlap. -->
        <div class="relative min-h-[20rem] flex-1">
          <div class="k-cosmos-halo" aria-hidden="true" />
          <HeroScene v-if="showScene && !sceneFailed && bands.length" :bands="bands" @unavailable="sceneFailed = true" />
        </div>
        <figure class="relative mt-8">
          <blockquote class="k-display text-[clamp(2.5rem,5vw,3.75rem)] leading-[0.95]">
            A better<br /><span class="k-serif text-[1.05em]">kind of</span><br /><span class="text-accent">busy.</span>
          </blockquote>
        </figure>
      </div>
    </div>
  </section>
  </div>

  <!-- 002 · HOW IT WORKS ----------------------------------------------------------- -->
  <section id="method" class="k-container scroll-mt-24 py-24 lg:py-32">
    <h2 class="k-story-head k-display text-[clamp(2.75rem,7.5vw,6.5rem)]">
      Preparation,<br /><span class="k-serif text-[1.05em]">reimagined.</span>
    </h2>
    <p class="mt-8 max-w-2xl text-lg leading-relaxed text-muted sm:text-xl">
      Progress is not a personality trait. It is a practice. KAFKA gives your preparation a place to become
      visible, repeatable, and yours.
    </p>
    <!-- Steps on one orbit line: horizontal from md up, vertical on phones. -->
    <ol class="k-story-steps relative mt-16 grid grid-cols-1 gap-12 md:grid-cols-3 md:gap-10 lg:mt-24">
      <span
        class="absolute top-[5px] bottom-0 left-[4px] w-px bg-gradient-to-b from-accent/50 via-accent/20 to-transparent md:top-[5px] md:right-0 md:bottom-auto md:left-0 md:h-px md:w-auto md:bg-gradient-to-r"
        aria-hidden="true"
      />
      <li v-for="step in steps" :key="step.n" class="k-story-step relative pl-8 md:pl-0">
        <span class="k-orbit-node absolute top-0 left-0 md:static" aria-hidden="true" />
        <p class="font-mono text-sm text-accent md:mt-8">{{ step.n }}</p>
        <h3 class="mt-3 text-2xl font-medium tracking-tight">{{ step.title }}</h3>
        <p class="mt-3 max-w-sm text-lg leading-relaxed text-muted">{{ step.body }}</p>
      </li>
    </ol>
  </section>

  <!-- 003 · TRACKS ------------------------------------------------------------------ -->
  <section id="prepare" class="k-container scroll-mt-24 pb-24 lg:pb-32">
    <div class="k-story-tracks grid grid-cols-1 gap-14 md:grid-cols-3 md:gap-10">
      <article v-for="track in tracks" :key="track.n" class="k-story-track border-t border-rule pt-8">
        <p class="font-mono text-sm">{{ track.n }}</p>
        <p class="k-serif my-10 text-center text-[7.5rem] leading-none not-italic" aria-hidden="true">{{ track.glyph }}</p>
        <h3 class="text-2xl font-medium tracking-tight uppercase">{{ track.title }}</h3>
        <p class="mt-4 max-w-sm text-lg leading-relaxed text-muted">{{ track.body }}</p>
        <div class="mt-8">
          <KArrowLink :to="startTo">Explore</KArrowLink>
        </div>
      </article>
    </div>
  </section>

  <!-- SHOW UP ------------------------------------------------------------------------- -->
  <!-- overflow-x-clip: the closing lines start slightly off-centre while they drift into place -->
  <section class="overflow-x-clip">
    <div class="k-container py-24 lg:py-32">
      <div class="grid grid-cols-1 items-start gap-14 xl:grid-cols-12 xl:items-end xl:gap-10">
        <h2 class="k-display min-w-0 text-[clamp(3.25rem,9vw,8.5rem)] xl:col-span-8">
          <span class="k-story-line block">Show up.</span>
          <span class="k-story-line k-serif block text-[1.02em] whitespace-nowrap text-accent not-italic">Get sharper.</span>
          <span class="k-story-line block">Go further.</span>
        </h2>
        <div class="min-w-0 xl:col-span-4 xl:pb-6">
          <div class="border-t border-rule pt-6">
            <p class="k-eyebrow mb-6 text-muted">This week</p>
            <KBarChart :data="week" label="Example questions per day" />
          </div>
          <p class="mt-10 flex items-baseline gap-4">
            <span class="k-serif text-6xl leading-none text-accent">07</span>
            <span class="k-label">Day streak</span>
          </p>
        </div>
      </div>
      <div class="mt-16">
        <KArrowLink :to="startTo">Enter Kafka</KArrowLink>
      </div>
    </div>
    <div class="k-container flex flex-col gap-3 border-t border-rule py-8 sm:flex-row sm:items-center sm:justify-between">
      <span class="k-display text-xl tracking-[-0.06em]">KAFKA<span class="text-accent">.</span></span>
      <p class="k-eyebrow text-muted">Built for placement season</p>
    </div>
  </section>
  </div>
</template>
