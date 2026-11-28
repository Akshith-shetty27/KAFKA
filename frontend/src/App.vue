<script setup>
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'

import KToaster from '@/components/ui/KToaster.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

// Which surface the whole page uses: fixed per route, or the user's theme
// inside the app. Sections can still flip locally with data-surface.
const surface = computed(() => {
  // Until the first navigation resolves (it waits for the session), keep the
  // surface index.html painted rather than flashing a default.
  if (!route.matched.length) return null
  const wanted = route.meta.surface ?? 'paper'
  return wanted === 'user' ? auth.theme : wanted
})

// Remember the signed-in user's theme so the next full page load starts on it,
// and forget it when nobody is signed in (so the next person doesn't inherit it).
watchEffect(() => {
  try {
    if (auth.user) localStorage.setItem('kafka:theme', auth.theme)
    else localStorage.removeItem('kafka:theme')
  } catch {
    /* storage unavailable: index.html falls back to Ink */
  }
})

watchEffect(() => {
  if (!surface.value) return
  document.documentElement.dataset.surface = surface.value
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', surface.value === 'ink' ? '#050505' : '#fffcf2')
})
</script>

<template>
  <RouterView />
  <KToaster />
</template>
