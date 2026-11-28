<script setup>
import { computed } from 'vue'

import KArrowLink from '@/components/ui/KArrowLink.vue'
import KLogo from '@/components/ui/KLogo.vue'
import { headerSurface } from '@/composables/useHeaderSurface'
import { publicNav } from '@/router/navigation'
import { useAuthStore } from '@/stores/auth'

import MobileMenu from './MobileMenu.vue'

const auth = useAuthStore()
const mobileItems = computed(() =>
  auth.isAuthenticated
    ? [...publicNav, { label: 'Dashboard', to: { name: 'dashboard' } }]
    : [...publicNav, { label: 'Sign in', to: { name: 'login' } }, { label: 'Start', to: { name: 'register' } }],
)
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-transparent backdrop-blur-md transition-colors duration-300"
    :class="headerSurface ? 'bg-black/70' : 'bg-canvas/90'"
    :data-surface="headerSurface || undefined"
  >
    <div class="k-container flex h-20 items-center justify-between gap-8 lg:h-24">
      <KLogo />

      <nav class="hidden items-center gap-10 lg:flex" aria-label="Primary">
        <RouterLink
          v-for="item in publicNav"
          :key="item.label"
          :to="item.to"
          class="k-label border-b border-transparent pb-1 transition-colors hover:border-fg"
        >
          {{ item.label }}
        </RouterLink>
        <RouterLink
          v-if="!auth.isAuthenticated"
          :to="{ name: 'login' }"
          class="k-label border-b border-transparent pb-1 transition-colors hover:border-fg"
        >
          Sign in
        </RouterLink>
      </nav>

      <div class="hidden lg:block">
        <KArrowLink v-if="auth.isAuthenticated" :to="{ name: 'dashboard' }">Go to dashboard</KArrowLink>
        <KArrowLink v-else :to="{ name: 'register' }">Start preparing</KArrowLink>
      </div>

      <MobileMenu :items="mobileItems" />
    </div>
  </header>
</template>
