<script setup>
/**
 * Profile & settings: personal details, preparation preferences (daily
 * goal drives today's plan, timezone drives streaks), theme, password.
 */
import { computed, reactive, ref } from 'vue'

import KButton from '@/components/ui/KButton.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KInput from '@/components/ui/KInput.vue'
import KSelect from '@/components/ui/KSelect.vue'
import { useForm } from '@/composables/useForm'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// --- profile & preferences -----------------------------------------------------
const profileForm = useForm()
const saved = ref(false)

function snapshot() {
  const u = auth.user
  return {
    first_name: u.first_name,
    last_name: u.last_name,
    profile: {
      college: u.profile.college,
      graduation_year: u.profile.graduation_year ?? '',
      target_role: u.profile.target_role,
      preferred_language: u.profile.preferred_language,
      daily_goal: u.profile.daily_goal,
      timezone: u.profile.timezone,
    },
  }
}
const form = reactive(snapshot())
const profileErrors = computed(() => profileForm.fieldErrors.profile ?? {})

const languages = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'javascript', label: 'JavaScript' },
]
const timezones = (() => {
  try {
    const all = Intl.supportedValuesOf('timeZone')
    return all.includes(form.profile.timezone) ? all : [form.profile.timezone, ...all]
  } catch {
    return [form.profile.timezone]
  }
})()

async function saveProfile() {
  saved.value = false
  const payload = {
    ...form,
    profile: {
      ...form.profile,
      graduation_year: form.profile.graduation_year === '' ? null : Number(form.profile.graduation_year),
      daily_goal: Number(form.profile.daily_goal),
    },
  }
  if (await profileForm.submit(() => auth.updateMe(payload))) {
    Object.assign(form, snapshot())
    saved.value = true
  }
}

// --- theme (saved immediately) ------------------------------------------------------
const themeForm = useForm()
async function setTheme(theme) {
  if (theme !== auth.theme) await themeForm.submit(() => auth.updateMe({ profile: { theme } }))
}

// --- password ------------------------------------------------------------------------
const passwordForm = useForm()
const passwords = reactive({ current_password: '', new_password: '' })
const passwordChanged = ref(false)

async function changePassword() {
  passwordChanged.value = false
  if (await passwordForm.submit(() => auth.changePassword({ ...passwords }))) {
    passwords.current_password = ''
    passwords.new_password = ''
    passwordChanged.value = true
  }
}
</script>

<template>
  <div class="k-container py-12 lg:py-16">
    <KEyebrow tone="muted">Settings</KEyebrow>
    <h1 class="k-display mt-6 text-[clamp(2.75rem,7vw,5.5rem)]">
      Make it<br /><span class="k-serif text-[1.05em]">yours.</span>
    </h1>

    <!-- Profile & preferences -->
    <form class="mt-16 grid grid-cols-1 gap-12 border-t border-rule pt-10 lg:grid-cols-12" novalidate @submit.prevent="saveProfile">
      <div class="lg:col-span-4">
        <KEyebrow as="h2" index="01">Profile</KEyebrow>
        <p class="mt-4 max-w-xs text-muted">Your daily goal shapes today's plan. Your timezone decides when a day — and a streak — ends.</p>
      </div>
      <div class="flex flex-col gap-6 lg:col-span-7 lg:col-start-6">
        <KErrorState v-if="profileForm.formError.value" :message="profileForm.formError.value" :retryable="false" />
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <KInput v-model="form.first_name" label="First name" autocomplete="given-name" :error="profileForm.fieldErrors.first_name" />
          <KInput v-model="form.last_name" label="Last name" autocomplete="family-name" :error="profileForm.fieldErrors.last_name" />
        </div>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <KInput v-model="form.profile.college" label="College" autocomplete="organization" :error="profileErrors.college" />
          <KInput
            v-model="form.profile.graduation_year"
            label="Graduation year"
            type="number"
            inputmode="numeric"
            min="1990"
            max="2100"
            :error="profileErrors.graduation_year"
          />
        </div>
        <KInput
          v-model="form.profile.target_role"
          label="Target role"
          placeholder="e.g. Software Engineer"
          :error="profileErrors.target_role"
        />
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <KInput
            v-model="form.profile.daily_goal"
            label="Daily goal"
            type="number"
            inputmode="numeric"
            min="1"
            max="50"
            hint="Questions per day"
            :error="profileErrors.daily_goal"
          />
          <KSelect v-model="form.profile.preferred_language" label="Language" :options="languages" :error="profileErrors.preferred_language" />
          <KSelect v-model="form.profile.timezone" label="Timezone" :options="timezones" :error="profileErrors.timezone" />
        </div>
        <div class="flex items-center gap-6">
          <KButton type="submit" :loading="profileForm.submitting.value">Save changes</KButton>
          <p v-if="saved" class="k-eyebrow text-accent-text" role="status">Saved</p>
        </div>
      </div>
    </form>

    <!-- Appearance -->
    <section class="mt-16 grid grid-cols-1 gap-12 border-t border-rule pt-10 lg:grid-cols-12">
      <div class="lg:col-span-4">
        <KEyebrow as="h2" index="02">Appearance</KEyebrow>
        <p class="mt-4 max-w-xs text-muted">Ink is easier on the eyes for long sessions. Paper matches the printed page.</p>
      </div>
      <div class="lg:col-span-7 lg:col-start-6">
        <div class="grid max-w-md grid-cols-2 gap-4" role="radiogroup" aria-label="Theme">
          <button
            v-for="option in [
              { value: 'ink', label: 'Ink', note: 'Dark' },
              { value: 'paper', label: 'Paper', note: 'Light' },
            ]"
            :key="option.value"
            type="button"
            role="radio"
            :aria-checked="auth.theme === option.value"
            :disabled="themeForm.submitting.value"
            class="group flex flex-col border p-4 text-left transition-colors"
            :class="auth.theme === option.value ? 'border-accent' : 'border-rule-soft hover:border-muted'"
            @click="setTheme(option.value)"
          >
            <span
              :data-surface="option.value"
              class="k-grid flex h-20 items-end justify-between border border-rule-soft p-3"
            >
              <span class="k-display text-lg tracking-[-0.06em]">K<span class="text-accent">.</span></span>
              <span class="h-6 w-10 bg-accent" />
            </span>
            <span class="mt-4 flex items-baseline justify-between">
              <span class="k-label">{{ option.label }}</span>
              <span class="text-sm text-muted">{{ option.note }}</span>
            </span>
          </button>
        </div>
        <KErrorState v-if="themeForm.formError.value" class="mt-4 max-w-md" :message="themeForm.formError.value" :retryable="false" />
      </div>
    </section>

    <!-- Password -->
    <form class="mt-16 grid grid-cols-1 gap-12 border-t border-rule pt-10 lg:grid-cols-12" novalidate @submit.prevent="changePassword">
      <div class="lg:col-span-4">
        <KEyebrow as="h2" index="03">Password</KEyebrow>
        <p class="mt-4 max-w-xs text-muted">Changing it signs you out on every other device.</p>
      </div>
      <div class="flex flex-col gap-6 lg:col-span-7 lg:col-start-6">
        <KErrorState v-if="passwordForm.formError.value" :message="passwordForm.formError.value" :retryable="false" />
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <KInput
            v-model="passwords.current_password"
            label="Current password"
            type="password"
            autocomplete="current-password"
            :error="passwordForm.fieldErrors.current_password"
          />
          <KInput
            v-model="passwords.new_password"
            label="New password"
            type="password"
            autocomplete="new-password"
            :error="passwordForm.fieldErrors.new_password"
          />
        </div>
        <div class="flex items-center gap-6">
          <KButton type="submit" variant="ghost" :loading="passwordForm.submitting.value">Change password</KButton>
          <p v-if="passwordChanged" class="k-eyebrow text-accent-text" role="status">Password changed</p>
        </div>
      </div>
    </form>

    <!-- Account -->
    <section class="mt-16 grid grid-cols-1 gap-12 border-t border-rule pt-10 lg:grid-cols-12">
      <div class="lg:col-span-4">
        <KEyebrow as="h2" index="04">Account</KEyebrow>
      </div>
      <dl class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:col-span-7 lg:col-start-6">
        <div>
          <dt class="k-eyebrow text-muted">Email</dt>
          <dd class="mt-2 break-all">{{ auth.user.email }}</dd>
        </div>
        <div>
          <dt class="k-eyebrow text-muted">Member since</dt>
          <dd class="mt-2">{{ new Date(auth.user.date_joined).toLocaleDateString('en', { month: 'long', year: 'numeric' }) }}</dd>
        </div>
      </dl>
    </section>
  </div>
</template>
