<script setup>
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import KButton from '@/components/ui/KButton.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KInput from '@/components/ui/KInput.vue'
import { useForm } from '@/composables/useForm'
import { useAuthStore } from '@/stores/auth'
import { browserTimezone, safeRedirect } from '@/utils/format'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { submitting, formError, fieldErrors, submit } = useForm()

const form = reactive({ first_name: '', last_name: '', email: '', password: '' })

async function onSubmit() {
  // The browser's timezone decides what "today" means for streaks.
  const ok = await submit(() => auth.register({ ...form, timezone: browserTimezone() }))
  if (ok) router.replace(safeRedirect(route.query.redirect))
}
</script>

<template>
  <KEyebrow index="00" tone="muted">Create account</KEyebrow>
  <h1 class="k-display mt-6 text-6xl sm:text-7xl">
    Start<br /><span class="k-serif text-[1.05em]">today.</span>
  </h1>
  <p class="mt-6 text-lg text-muted">Two minutes now. A plan for every day after.</p>

  <form class="mt-10 flex flex-col gap-6" novalidate @submit.prevent="onSubmit">
    <KErrorState v-if="formError" :message="formError" :retryable="false" />
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <KInput
        v-model="form.first_name"
        label="First name"
        autocomplete="given-name"
        required
        :error="fieldErrors.first_name"
      />
      <KInput v-model="form.last_name" label="Last name" autocomplete="family-name" :error="fieldErrors.last_name" />
    </div>
    <KInput v-model="form.email" label="Email" type="email" autocomplete="email" required :error="fieldErrors.email" />
    <KInput
      v-model="form.password"
      label="Password"
      type="password"
      autocomplete="new-password"
      required
      hint="At least 8 characters. Avoid common passwords."
      :error="fieldErrors.password"
    />
    <KButton type="submit" :loading="submitting" block icon="arrow-up-right">Create account</KButton>
  </form>

  <p class="mt-10 text-sm text-muted">
    Already preparing with us?
    <RouterLink :to="{ name: 'login' }" class="ml-1 font-medium text-fg underline underline-offset-4 hover:text-accent-text">
      Sign in
    </RouterLink>
  </p>
</template>
