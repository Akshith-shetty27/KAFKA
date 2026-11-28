<script setup>
/**
 * ASK KAFKA → new study plan. The student pastes a job description, names the
 * role (and optionally company, background and time left); the server turns
 * it into a prioritised, JD-specific roadmap and we open it.
 */
import { onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import KAssistantMark from '@/components/assistant/KAssistantMark.vue'
import KButton from '@/components/ui/KButton.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KIcon from '@/components/ui/KIcon.vue'
import KInput from '@/components/ui/KInput.vue'
import KTextarea from '@/components/ui/KTextarea.vue'
import { useForm } from '@/composables/useForm'
import { prepApi } from '@/services/prep.api'
import { useAuthStore } from '@/stores/auth'

const MIN_JD = 200
const MAX_JD = 15000

const auth = useAuthStore()
const router = useRouter()
const { submitting, formError, fieldErrors, submit } = useForm()

const form = reactive({
  role: auth.user?.profile?.target_role ?? '',
  company: '',
  job_description: '',
  candidate_info: '',
  days_available: '',
  hours_per_day: '',
})

// What the server is doing during the ~10 s generation, so the wait reads as progress.
const stages = ['Reading the job description…', 'Picking out the requirements…', 'Prioritising for your time…', 'Building your roadmap…']
const stage = ref(0)
let timer = null
watch(submitting, (busy) => {
  clearInterval(timer)
  stage.value = 0
  if (busy) timer = setInterval(() => (stage.value = Math.min(stage.value + 1, stages.length - 1)), 3500)
})
onBeforeUnmount(() => clearInterval(timer))

function numberOrNull(value) {
  return value === '' || value === null ? null : Number(value)
}

async function generate() {
  let created = null
  const ok = await submit(async () => {
    created = await prepApi.create({
      role: form.role.trim(),
      company: form.company.trim(),
      job_description: form.job_description,
      candidate_info: form.candidate_info.trim(),
      days_available: numberOrNull(form.days_available),
      hours_per_day: numberOrNull(form.hours_per_day),
    })
  })
  if (ok && created) router.push({ name: 'plan', params: { id: created.id } })
}

const steps = [
  ['Paste', 'the full job description — responsibilities, required skills, interview process.'],
  ['Analyse', 'KAFKA pulls out every requirement and quotes the line it came from.'],
  ['Plan', 'a phased roadmap — fundamentals to mock interviews — sized to your time.'],
  ['Practise', 'each item links straight to KAFKA topics and patterns, and tracks your progress.'],
]
</script>

<template>
  <div class="k-container grid grid-cols-1 gap-12 py-10 lg:grid-cols-12 lg:py-12">
    <section class="lg:col-span-8" aria-labelledby="plan-new-title">
      <RouterLink :to="{ name: 'ask' }" class="k-eyebrow inline-flex items-center gap-2 text-muted hover:text-fg">
        <KIcon name="arrow-left" :size="12" /> Ask Kafka
      </RouterLink>
      <h1 id="plan-new-title" class="k-display mt-6 text-[clamp(2.5rem,6vw,4.5rem)]">
        Paste the job.<br /><span class="k-serif text-[1.05em]">Get the plan.</span>
      </h1>
      <p class="mt-5 max-w-xl text-lg text-muted">
        KAFKA reads the job description and builds a preparation plan for that exact role — not a generic checklist.
      </p>

      <form class="mt-10 flex flex-col gap-7" novalidate @submit.prevent="generate">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <KInput v-model="form.role" label="Role" required placeholder="e.g. Software Engineer I – Backend" :error="fieldErrors.role" />
          <KInput v-model="form.company" label="Company" placeholder="Optional" :error="fieldErrors.company" />
        </div>

        <KTextarea
          v-model="form.job_description"
          label="Job description"
          required
          :rows="14"
          :maxlength="MAX_JD"
          show-count
          placeholder="Paste the whole posting here: about the role, responsibilities, requirements, nice-to-haves, interview process…"
          :error="fieldErrors.job_description"
          :hint="`At least ${MIN_JD} characters. Text inside the description is treated as data, never as instructions.`"
        />

        <KTextarea
          v-model="form.candidate_info"
          label="About you"
          :rows="3"
          :maxlength="2000"
          placeholder="Optional — e.g. final-year CSE, comfortable in Python, weak at graphs and DP, no system design yet."
          :error="fieldErrors.candidate_info"
          hint="Helps KAFKA spend more time on your weak areas."
        />

        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <KInput
            v-model="form.days_available"
            label="Days until the interview"
            type="number"
            inputmode="numeric"
            min="1"
            max="180"
            placeholder="Optional"
            :error="fieldErrors.days_available"
          />
          <KInput
            v-model="form.hours_per_day"
            label="Hours per day"
            type="number"
            inputmode="numeric"
            min="1"
            max="12"
            placeholder="2"
            :error="fieldErrors.hours_per_day"
            hint="Used with the days to size the plan."
          />
        </div>

        <KErrorState v-if="formError" :message="formError" :retryable="false" />

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
          <KButton type="submit" :loading="submitting" :disabled="submitting">Generate my preparation plan</KButton>
          <div v-if="submitting" class="flex items-start gap-3" aria-live="polite">
            <KAssistantMark active :size="18" class="mt-0.5" />
            <div>
              <p class="text-sm">{{ stages[stage] }}</p>
              <!-- Stage dots: done · current · upcoming (purely visual; the text above is announced) -->
              <p class="mt-2 flex gap-1.5" aria-hidden="true">
                <span
                  v-for="(s, i) in stages"
                  :key="s"
                  class="h-[3px] w-6 transition-colors duration-500"
                  :class="i < stage ? 'bg-accent' : i === stage ? 'bg-accent/50' : 'bg-rule-soft'"
                />
              </p>
              <p class="mt-2 text-xs text-muted">This usually takes about 10 seconds.</p>
            </div>
          </div>
        </div>
      </form>
    </section>

    <aside class="lg:col-span-4 lg:pt-28" aria-label="How it works">
      <KEyebrow tone="muted">How it works</KEyebrow>
      <ol class="mt-6 flex flex-col">
        <li v-for="([title, text], i) in steps" :key="title" class="flex gap-5 border-t border-rule-soft py-5">
          <span class="font-mono text-sm text-muted">{{ String(i + 1).padStart(2, '0') }}</span>
          <p class="text-sm leading-relaxed text-muted"><span class="font-medium text-fg">{{ title }}</span> {{ text }}</p>
        </li>
      </ol>
    </aside>
  </div>
</template>
