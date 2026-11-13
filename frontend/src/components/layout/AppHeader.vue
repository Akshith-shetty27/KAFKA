<script setup>
import { useRouter } from 'vue-router'

import KIcon from '@/components/ui/KIcon.vue'
import KLogo from '@/components/ui/KLogo.vue'
import { appNav } from '@/router/navigation'
import { useAuthStore } from '@/stores/auth'

import MobileMenu from './MobileMenu.vue'

const auth = useAuthStore()
const router = useRouter()

async function signOut() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-rule-soft bg-canvas/90 backdrop-blur-md">
    <div class="k-container flex h-20 items-center justify-between gap-8">
      <KLogo :to="{ name: 'dashboard' }" />

      <nav class="hidden items-center gap-10 lg:flex" aria-label="Primary">
        <RouterLink
          v-for="item in appNav"
          :key="item.label"
          :to="item.to"
          class="k-label inline-flex items-center gap-2 border-b border-transparent pb-1 transition-colors hover:text-fg"
          active-class="!border-fg"
        >
          <KIcon v-if="item.icon" :name="item.icon" :size="15" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="hidden items-center gap-6 lg:flex">
        <span class="k-eyebrow max-w-48 truncate text-muted" :title="auth.user?.email">{{ auth.displayName }}</span>
        <button type="button" class="k-label inline-flex items-center gap-2 hover:text-accent-text" @click="signOut">
          Sign out <KIcon name="logout" :size="15" />
        </button>
      </div>

      <MobileMenu :items="appNav">
        <template #footer>
          <p class="k-eyebrow text-muted">{{ auth.user?.email }}</p>
          <button type="button" class="k-label mt-4 inline-flex items-center gap-2 text-accent" @click="signOut">
            Sign out <KIcon name="logout" :size="15" />
          </button>
        </template>
      </MobileMenu>
    </div>
  </header>
</template>
