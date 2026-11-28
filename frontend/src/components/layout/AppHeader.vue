<script setup>
import { useRoute, useRouter } from 'vue-router'

import KIcon from '@/components/ui/KIcon.vue'
import KLogo from '@/components/ui/KLogo.vue'
import { appNav } from '@/router/navigation'
import { useAuthStore } from '@/stores/auth'

import MobileMenu from './MobileMenu.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

function isActive(item) {
  if (item.match) return item.match.some((prefix) => route.path.startsWith(prefix))
  return router.resolve(item.to).path === route.path
}

async function signOut() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-rule-soft bg-canvas/90 backdrop-blur-md">
    <!-- Tighter gaps from lg (1024px) up to xl, so six links + name + sign out fit on one line. -->
    <div class="k-container flex h-20 items-center justify-between gap-6 xl:gap-8">
      <KLogo :to="{ name: 'dashboard' }" />

      <nav class="hidden items-center gap-6 lg:flex xl:gap-10" aria-label="Primary">
        <RouterLink
          v-for="item in appNav"
          :key="item.label"
          :to="item.to"
          class="k-label inline-flex items-center gap-2 border-b pb-1 whitespace-nowrap transition-colors hover:text-fg"
          :class="isActive(item) ? 'border-fg' : 'border-transparent'"
          :aria-current="isActive(item) ? 'page' : undefined"
        >
          <KIcon v-if="item.icon" :name="item.icon" :size="15" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="hidden min-w-0 items-center gap-5 lg:flex xl:gap-6">
        <!-- The name only shows from xl up; between lg and xl there's no room for it. -->
        <span class="k-eyebrow hidden max-w-48 truncate text-muted xl:inline" :title="auth.user?.email">{{ auth.displayName }}</span>
        <button type="button" class="k-label inline-flex shrink-0 items-center gap-2 whitespace-nowrap hover:text-accent-text" @click="signOut">
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
