<script setup>
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import KButton from '@/components/ui/KButton.vue'
import KErrorState from '@/components/ui/KErrorState.vue'
import KEyebrow from '@/components/ui/KEyebrow.vue'
import KInput from '@/components/ui/KInput.vue'
import { useForm } from '@/composables/useForm'
import { useAuthStore } from '@/stores/auth'
import { safeRedirect } from '@/utils/format'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { submitting, formError, fieldErrors, submit } = useForm()

const form = reactive({ email: '', password: '' })
const sessionExpired = route.query.expired === '1'

async function onSubmit() {
  const ok = await submit(() => auth.login({ ...form }))
  if (ok) router.replace(safeRedirect(route.query.redirect))
}
</script>

<template>
  <KEyebrow tone="muted">Sign in</KEyebrow>
  <h1 class="k-display mt-6 text-6xl sm:text-7xl">
    Welcome<br /><span class="k-serif text-[1.05em]">back.</span>
  </h1>
  <p class="mt-6 text-lg text-muted">Pick up exactly where you left off.</p>

  <p v-if="sessionExpired && !formError" class="mt-8 border-l-2 border-warning pl-4 text-sm" role="status">
    Your session expired. Sign in again to continue.
  </p>

  <form class="mt-10 flex flex-col gap-6" novalidate @submit.prevent="onSubmit">
    <KErrorState v-if="formError" :message="formError" :retryable="false" />
    <KInput v-model="form.email" label="Email" type="email" autocomplete="email" required :error="fieldErrors.email" />
    <KInput
      v-model="form.password"
      label="Password"
      type="password"
      autocomplete="current-password"
      required
      :error="fieldErrors.password"
    />
    <KButton type="submit" :loading="submitting" block icon="arrow-up-right">Sign in</KButton>
  </form>

  <p class="mt-10 text-sm text-muted">
    New to KAFKA?
    <RouterLink :to="{ name: 'register', query: route.query.redirect ? { redirect: route.query.redirect } : {} }" class="ml-1 font-medium text-fg underline underline-offset-4 hover:text-accent-text">
      Create an account
    </RouterLink>
  </p>
</template>
