<script setup>
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

// Which surface the whole page uses: fixed per route, or the user's theme
// inside the app. Sections can still flip locally with data-surface.
const surface = computed(() => {
  const wanted = route.meta.surface ?? 'paper'
  return wanted === 'user' ? auth.theme : wanted
})

watchEffect(() => {
  document.documentElement.dataset.surface = surface.value
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', surface.value === 'ink' ? '#050505' : '#fffcf2')
})
</script>

<template>
  <RouterView />
</template>
