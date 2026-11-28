<script setup>
/**
 * Split screen: the form on Paper (left), the hero's Ink panel (right, from
 * the reference) on large screens. Switching between sign-in and register
 * uses the app's page transition; the panel shows the real bank size.
 */
import { onMounted, ref } from 'vue'

import KCodeWindow from '@/components/ui/KCodeWindow.vue'
import KLogo from '@/components/ui/KLogo.vue'
import { catalogApi } from '@/services/catalog.api'

const stats = ref(null)
onMounted(async () => {
  try {
    stats.value = await catalogApi.stats()
  } catch {
    stats.value = null // decorative only; the panel works without it
  }
})

const lines = [
  [{ t: 'const', k: 'kw' }, { t: ' plan ' }, { t: '=', k: 'op' }, { t: ' kafka.' }, { t: 'today', k: 'fn' }, { t: '();' }],
  [{ t: 'plan.' }, { t: 'coding', k: 'fn' }, { t: '(' }, { t: '"sliding-window"', k: 'str' }, { t: ');' }],
  [{ t: 'plan.' }, { t: 'aptitude', k: 'fn' }, { t: '(' }, { t: '"time-and-work"', k: 'str' }, { t: ');' }],
  [{ t: 'return', k: 'kw' }, { t: ' plan.' }, { t: 'showUp', k: 'fn' }, { t: '();' }],
]
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
      <div class="k-rise flex items-start justify-between gap-6">
        <div>
          <p class="font-mono text-lg text-accent">K / 01</p>
          <p class="k-label mt-4 leading-loose">Build your<br />edge</p>
        </div>
        <p v-if="stats" class="text-right font-mono text-xs leading-relaxed text-muted">
          {{ stats.total }} questions<br />{{ stats.tracks.length }} tracks
        </p>
      </div>
      <div class="k-rise px-6" style="--i: 2">
        <KCodeWindow :lines="lines" status="Plan ready" meta="5 tasks" />
      </div>
      <p class="k-rise k-display text-6xl xl:text-7xl" style="--i: 4">
        Show up.<br /><span class="k-serif text-accent">get sharper.</span>
      </p>
    </aside>
  </div>
</template>
