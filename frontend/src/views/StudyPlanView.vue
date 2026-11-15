<script setup>
/**
 * One study plan: what the job asks for (with the quoted evidence), then the
 * phased roadmap. Items are ticked off here; linked topics show the student's
 * real progress and open Practice filtered to that topic or pattern.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import KEmptyState from '@/components/ui/KEmptyState.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KIcon from '@/components/ui/KIcon.vue'
import KProgressBar from '@/components/ui/KProgressBar.vue'
import KSkeleton from '@/components/ui/KSkeleton.vue'
import { prepApi } from '@/services/prep.api'
import { toApiError } from '@/services/http'

const route = useRoute()
const router = useRouter()

const plan = ref(null)
const loading = ref(false)
const error = ref(null)
const saveError = ref('')
const pending = ref(new Set())

async function load(id) {
  loading.value = true
  error.value = null
  try {
    plan.value = await prepApi.get(id)
  } catch (err) {
    error.value = err.apiError ?? toApiError(err)
  } finally {
    loading.value = false
  }
}
watch(() => route.params.id, (id) => id && load(id), { immediate: true })

const progress = computed(() => {
  const items = plan.value?.phases.flatMap((p) => p.items) ?? []
  const done = items.filter((i) => i.completed)
  return {
    done: done.length,
    total: items.length,
    hoursDone: done.reduce((sum, i) => sum + i.est_hours, 0),
    hours: items.reduce((sum, i) => sum + i.est_hours, 0),
  }
})

async function toggle(item) {
  if (pending.value.has(item.id)) return
  const next = !item.completed
  item.completed = next // optimistic
  pending.value.add(item.id)
  saveError.value = ''
  try {
    await prepApi.setItemCompleted(plan.value.id, item.id, next)
  } catch (err) {
    item.completed = !next
    saveError.value = (err.apiError ?? toApiError(err)).message
  } finally {
    pending.value.delete(item.id)
  }
}

async function remove() {
  if (!window.confirm(`Delete the study plan for “${plan.value.role}”? This can't be undone.`)) return
  try {
    await prepApi.remove(plan.value.id)
    router.push({ name: 'ask' })
  } catch (err) {
    saveError.value = (err.apiError ?? toApiError(err)).message
  }
}

const importanceTone = { high: 'bg-danger', medium: 'bg-warning', low: 'bg-accent' }
function createdOn(iso) {
  return new Date(iso).toLocaleDateString('en', { day: 'numeric', month: 'long', year: 'numeric' })
}
function hours(n) {
  return `${Number.isInteger(n) ? n : n.toFixed(1)} h`
}
function topicLink(t) {
  return { name: 'practice', params: { category: t.category }, query: { topic: t.slug } }
}
function patternLink(p) {
  return { name: 'practice', params: { category: 'coding' }, query: { pattern: p.slug } }
}
</script>

<template>
  <div class="k-container py-10 lg:py-12">
    <RouterLink :to="{ name: 'ask' }" class="k-eyebrow inline-flex items-center gap-2 text-muted hover:text-fg">
      <KIcon name="arrow-left" :size="12" /> Ask Kafka
    </RouterLink>

    <KEmptyState v-if="error?.status === 404" class="mt-10" title="Study plan not found">
      It may have been deleted. <RouterLink :to="{ name: 'plan-new' }" class="underline underline-offset-4">Create a new one</RouterLink>.
    </KEmptyState>
    <KErrorState v-else-if="error" class="mt-10" :message="error.message" @retry="load(route.params.id)" />
    <div v-else-if="loading || !plan" class="mt-10"><KSkeleton :lines="8" height="1.5rem" /></div>

    <template v-else>
      <!-- Header -->
      <header class="mt-6 grid grid-cols-1 gap-10 border-b border-rule pb-10 lg:grid-cols-12">
        <div class="min-w-0 lg:col-span-8">
          <KEyebrow tone="muted">Study plan · {{ createdOn(plan.created_at) }}</KEyebrow>
          <h1 class="k-display mt-4 text-[clamp(2.25rem,5vw,4rem)] break-words normal-case">
            {{ plan.role }}<template v-if="plan.company"><span class="k-serif text-[1.05em]"> at</span> {{ plan.company }}</template>
          </h1>
          <p class="mt-5 max-w-2xl text-lg leading-relaxed text-muted">{{ plan.summary }}</p>
          <p v-if="plan.model === 'kafka-offline-demo'" class="mt-4 text-sm text-warning">
            Offline demo plan — set up the AI provider on the server for a real analysis.
          </p>
        </div>
        <div class="flex flex-col justify-end gap-4 lg:col-span-4">
          <p class="flex items-baseline justify-between font-mono text-sm">
            <span>{{ progress.done }}/{{ progress.total }} items</span>
            <span class="text-muted">{{ hours(progress.hoursDone) }} of {{ hours(progress.hours) }}</span>
          </p>
          <KProgressBar :value="progress.done" :max="progress.total" label="Plan progress" />
          <p class="text-sm text-muted">
            <template v-if="plan.days_available">{{ plan.days_available }} days · {{ plan.hours_per_day ?? 2 }} h/day</template>
            <template v-else>No deadline set</template>
          </p>
          <div class="flex flex-wrap gap-x-6 gap-y-2">
            <RouterLink :to="{ name: 'plan-new' }" class="k-eyebrow text-muted hover:text-accent-text">New plan</RouterLink>
            <button type="button" class="k-eyebrow text-muted hover:text-danger" @click="remove">Delete plan</button>
          </div>
        </div>
      </header>

      <KErrorState v-if="saveError" class="mt-6" :message="saveError" :retryable="false" />

      <div class="mt-12 grid grid-cols-1 gap-14 lg:grid-cols-12">
        <!-- What the job asks for -->
        <section class="order-2 lg:order-none lg:col-span-4" aria-labelledby="reqs-title">
          <KEyebrow id="reqs-title" as="h2">The job asks for</KEyebrow>
          <ul class="mt-6 flex flex-col">
            <li v-for="req in plan.requirements" :key="req.skill" class="border-t border-rule-soft py-4">
              <p class="flex items-start gap-3">
                <span class="mt-2 size-1.5 shrink-0 rounded-full" :class="importanceTone[req.importance]" aria-hidden="true" />
                <span class="font-medium">{{ req.skill }}</span>
              </p>
              <p class="mt-1 pl-[18px] font-mono text-[11px] tracking-wide text-muted uppercase">{{ req.importance }} priority</p>
              <blockquote class="mt-2 ml-[18px] border-l border-rule pl-3 text-sm text-muted italic">“{{ req.evidence }}”</blockquote>
            </li>
          </ul>
          <details class="mt-6 border-t border-rule-soft pt-4">
            <summary class="k-eyebrow cursor-pointer text-muted hover:text-fg">Job description</summary>
            <p v-if="plan.jd_truncated" class="mt-3 text-sm text-warning">Long description — only the first part was analysed.</p>
            <p class="mt-3 max-h-96 overflow-y-auto text-sm leading-relaxed whitespace-pre-line text-muted">{{ plan.job_description }}</p>
          </details>
        </section>

        <!-- Roadmap -->
        <section class="order-1 min-w-0 lg:order-none lg:col-span-8" aria-labelledby="roadmap-title">
          <KEyebrow id="roadmap-title" as="h2">Your roadmap</KEyebrow>
          <ol class="mt-6 flex flex-col gap-12">
            <li v-for="(phase, p) in plan.phases" :key="phase.id">
              <header class="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-t border-rule pt-5">
                <h3 class="text-2xl font-medium tracking-tight">
                  <span class="mr-3 font-mono text-base text-muted">{{ String(p + 1).padStart(2, '0') }}</span>{{ phase.title }}
                </h3>
                <span class="font-mono text-sm text-muted">{{ phase.kind_label }} · {{ hours(phase.est_hours) }}</span>
              </header>
              <p v-if="phase.goal" class="mt-2 text-muted">{{ phase.goal }}</p>

              <ul class="mt-5 flex flex-col gap-3">
                <li v-for="item in phase.items" :key="item.id" class="bg-surface p-5 transition-opacity" :class="item.completed ? 'opacity-70' : ''">
                  <div class="flex items-start gap-4">
                    <button
                      type="button"
                      class="mt-0.5 flex size-6 shrink-0 items-center justify-center border transition-colors"
                      :class="item.completed ? 'border-accent bg-accent text-on-accent' : 'border-muted hover:border-accent'"
                      :aria-pressed="item.completed"
                      :aria-label="`${item.completed ? 'Mark not done' : 'Mark done'}: ${item.title}`"
                      :disabled="pending.has(item.id)"
                      @click="toggle(item)"
                    >
                      <KIcon v-if="item.completed" name="check" :size="14" />
                    </button>
                    <div class="min-w-0 flex-1">
                      <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                        <h4 class="min-w-0 text-lg font-medium tracking-tight break-words" :class="item.completed ? 'line-through decoration-1' : ''">{{ item.title }}</h4>
                        <span class="shrink-0 font-mono text-sm text-muted">{{ hours(item.est_hours) }}</span>
                      </div>
                      <p class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] tracking-wide text-muted uppercase">
                        <span class="inline-flex items-center gap-2">
                          <span class="size-1.5 rounded-full" :class="importanceTone[item.importance]" aria-hidden="true" />{{ item.importance }}
                        </span>
                        <span>{{ item.category_label }}</span>
                      </p>
                      <p class="mt-3 text-sm leading-relaxed">{{ item.reason }}</p>

                      <ul v-if="item.subtopics.length" class="mt-4 flex flex-wrap gap-2" aria-label="Subtopics">
                        <li v-for="s in item.subtopics" :key="s" class="border border-rule-soft px-2 py-1 text-xs text-muted">{{ s }}</li>
                      </ul>
                      <ul v-if="item.activities.length" class="mt-4 flex flex-col gap-1.5 text-sm" aria-label="Activities">
                        <li v-for="a in item.activities" :key="a" class="flex gap-2">
                          <span class="text-accent-text" aria-hidden="true">→</span><span>{{ a }}</span>
                        </li>
                      </ul>

                      <div v-if="item.topics.length || item.patterns.length" class="mt-5 flex flex-wrap gap-2 border-t border-rule-soft pt-4">
                        <RouterLink
                          v-for="t in item.topics"
                          :key="t.slug"
                          :to="topicLink(t)"
                          class="k-label inline-flex items-center gap-2 bg-raised px-3 py-2 text-[11px] hover:text-accent-text"
                        >
                          {{ t.name }} <span class="font-mono text-muted">{{ t.completed_count }}/{{ t.question_count }}</span>
                          <KIcon name="arrow-up-right" :size="12" />
                        </RouterLink>
                        <RouterLink
                          v-for="pt in item.patterns"
                          :key="pt.slug"
                          :to="patternLink(pt)"
                          class="k-label inline-flex items-center gap-2 border border-rule-soft px-3 py-2 text-[11px] hover:text-accent-text"
                        >
                          Pattern · {{ pt.name }} <KIcon name="arrow-up-right" :size="12" />
                        </RouterLink>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </li>
          </ol>
        </section>
      </div>
    </template>
  </div>
</template>
