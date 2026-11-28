<script setup>
/**
 * Split screen: the form on Paper (left), the hero's Ink panel (right, from
 * the reference) on large screens. Switching between sign-in and register
 * uses the app's page transition. The panel greets the visitor (italic letters
 * cascading in, then a teal underline) above KAFKA's waving robot; both replay
 * on a page switch.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import GreetingCascade from '@/components/auth/GreetingCascade.vue'
import WavingBot from '@/components/auth/WavingBot.vue'
import KLogo from '@/components/ui/KLogo.vue'

const route = useRoute()
const greeting = computed(() => (route.name === 'register' ? 'Hey there' : 'Welcome back'))
</script>

<template>
  <div class="grid grid-cols-1 min-h-screen lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
    <div class="flex flex-col px-4 py-6 sm:px-10 lg:px-16">
      <header class="flex h-14 items-center">
        <KLogo />
      </header>
      <main id="main" class="flex flex-1 items-center py-12">
        <div class="w-full max-w-md">
          <RouterView v-slot="{ Component }">
            <Transition name="k-page" mode="out-in">
              <component :is="Component" />
            </Transition>
          </RouterView>
        </div>
      </main>
    </div>

    <aside data-surface="ink" class="k-grid relative hidden flex-col justify-between overflow-hidden p-14 lg:flex" aria-hidden="true">
      <GreetingCascade :key="greeting" :text="greeting" class="self-start" />
      <div class="k-rise" style="--i: 2">
        <WavingBot :greeting="greeting" :bubble="false" />
      </div>
      <p class="k-rise k-display text-6xl xl:text-7xl" style="--i: 4">
        Show up.<br /><span class="k-serif text-accent">get sharper.</span>
      </p>
    </aside>
  </div>
</template>
