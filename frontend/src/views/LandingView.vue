<script setup>
/**
 * Public landing page, built from the reference screenshots:
 *   001 hero · 002 the KAFKA method · 003 the three tracks ·
 *   004 ASK KAFKA · "show up" closing section.
 * Numbers here (07-day streak, weekly bars) are illustrative marketing
 * visuals, not user data — the dashboard shows the real thing.
 */
import { computed } from 'vue'

import KArrowLink from '@/components/ui/KArrowLink.vue'
import KBarChart from '@/components/ui/KBarChart.vue'
import KChecklist from '@/components/ui/KChecklist.vue'
import KCodeWindow from '@/components/ui/KCodeWindow.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KStreakBadge from '@/components/ui/KStreakBadge.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const startTo = computed(() => (auth.isAuthenticated ? { name: 'dashboard' } : { name: 'register' }))

const heroCode = [
  [{ t: 'function', k: 'kw' }, { t: ' solve', k: 'fn' }, { t: '(input) {' }],
  [{ t: '  const', k: 'kw' }, { t: ' focus ' }, { t: '=', k: 'op' }, { t: ' "consistency"', k: 'str' }, { t: ';' }],
  [{ t: '  return', k: 'kw' }, { t: ' focus ' }, { t: '+', k: 'op' }, { t: ' input;' }],
  [{ t: '}' }],
]

const samplePlan = [
  { key: 'c', label: '2 coding problems', done: true },
  { key: 'a', label: '15 aptitude questions', done: true },
  { key: 'r', label: '3 core CS concepts', done: false, tag: 'Next' },
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
  <!-- 001 · HERO ---------------------------------------------------------- -->
  <section class="k-container grid grid-cols-1 gap-14 pt-10 pb-20 lg:grid-cols-12 lg:gap-10 lg:pt-16 lg:pb-28">
    <div class="lg:col-span-7">
      <KEyebrow index="001" class="k-rise">Interview preparation</KEyebrow>
      <h1 class="k-display mt-8 text-[clamp(3.4rem,10.5vw,8.25rem)] lg:mt-12">
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
      <div data-surface="ink" class="k-grid k-rise relative flex h-full min-h-[34rem] flex-col p-7 sm:p-10 lg:p-8 xl:p-10" style="--i: 3">
        <p class="font-mono text-lg text-accent">K / 01</p>
        <p class="k-label mt-4 leading-[2.2]">Build your<br />edge</p>

        <div class="my-10 sm:mx-4">
          <KCodeWindow :lines="heroCode" status="12 tests passed" meta="98ms" />
        </div>

        <div class="mt-auto flex flex-wrap items-end justify-between gap-4 sm:flex-nowrap">
          <p class="k-display text-[2.75rem] leading-[0.92] lg:text-[2.5rem] xl:text-5xl">
            Make<br /><span class="k-serif">room</span><br />for<br /><span class="text-accent">more.</span>
          </p>
          <KStreakBadge :days="7" />
        </div>
      </div>
    </div>
  </section>

  <!-- 002 · THE KAFKA METHOD -------------------------------------------------- -->
  <section id="method" class="k-container grid grid-cols-1 scroll-mt-24 gap-14 py-20 lg:grid-cols-12 lg:gap-10 lg:py-28">
    <div class="lg:col-span-4">
      <KEyebrow index="002">The Kafka method</KEyebrow>
      <div class="mt-14">
        <KChecklist :items="samplePlan" title="Today's plan" />
      </div>
    </div>
    <div class="lg:col-span-7 lg:col-start-6">
      <h2 class="k-display text-[clamp(2.75rem,7.5vw,6.5rem)]">
        Preparation,<br /><span class="k-serif text-[1.05em]">reimagined.</span>
      </h2>
      <p class="mt-10 max-w-2xl text-lg leading-relaxed sm:text-xl">
        Progress is not a personality trait. It is a practice. KAFKA gives your preparation a place to become
        visible, repeatable, and yours.
      </p>
    </div>
  </section>

  <!-- 003 · TRACKS ------------------------------------------------------------------ -->
  <section id="prepare" class="k-container scroll-mt-24 pb-24 lg:pb-32">
    <KEyebrow index="003" tone="muted" class="mb-10">Three tracks</KEyebrow>
    <div class="grid grid-cols-1 gap-14 md:grid-cols-3 md:gap-10">
      <article v-for="track in tracks" :key="track.n" class="border-t border-rule pt-8">
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

  <!-- 004 · ASK KAFKA ---------------------------------------------------------------- -->
  <section id="ask-kafka" class="scroll-mt-20 border-t border-rule bg-surface">
    <div class="k-container grid grid-cols-1 gap-14 py-20 lg:grid-cols-12 lg:gap-10 lg:py-28">
      <div class="lg:col-span-5">
        <KEyebrow index="004">Ask Kafka</KEyebrow>
        <h2 class="k-display mt-8 text-[clamp(2.75rem,6.5vw,5.5rem)]">
          Hints,<br />not <span class="k-serif text-[1.05em]">spoilers.</span>
        </h2>
        <p class="mt-8 max-w-md text-lg leading-relaxed">
          An AI mentor that reads the problem you're on. It nudges you toward the pattern first — and only walks
          through the full solution when you ask.
        </p>
      </div>
      <div class="lg:col-span-6 lg:col-start-7">
        <div data-surface="ink" class="k-grid flex flex-col gap-5 p-6 sm:p-10" aria-label="Example conversation" role="img">
          <p class="k-eyebrow text-muted">Longest substring without repeats</p>
          <div class="ml-auto max-w-[85%] bg-ink-800 px-5 py-4 text-[15px] leading-relaxed">
            I keep restarting my loop every time I see a repeat. It's too slow.
          </div>
          <div class="max-w-[90%] border-l-2 border-accent pl-5 text-[15px] leading-relaxed">
            <p class="k-eyebrow mb-3 text-accent">Kafka · hint 1 of 3</p>
            What if you never restarted? Keep a window of characters with no repeats, and only move its
            <em class="k-serif text-lg">left</em> edge when a repeat forces you to.
          </div>
          <div class="ml-auto max-w-[85%] bg-ink-800 px-5 py-4 text-[15px] leading-relaxed">So it's a sliding window?</div>
          <div class="max-w-[90%] border-l-2 border-accent pl-5 text-[15px] leading-relaxed">
            <p class="k-eyebrow mb-3 text-accent">Kafka · hint 2 of 3</p>
            Exactly. Now: how would you know, in O(1), where the last copy of a character was?
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- SHOW UP ------------------------------------------------------------------------- -->
  <section data-surface="ink">
    <div class="k-container py-24 lg:py-32">
      <KEyebrow>A better kind of busy</KEyebrow>
      <div class="mt-14 grid grid-cols-1 items-end gap-14 lg:grid-cols-12 lg:gap-10">
        <h2 class="k-display text-[clamp(3.25rem,10vw,8.5rem)] lg:col-span-8">
          Show up.<br />
          <span class="k-serif text-[1.02em] whitespace-nowrap text-accent not-italic">Get sharper.</span><br />
          Go further.
        </h2>
        <div class="lg:col-span-4 lg:pb-6">
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
</template>
