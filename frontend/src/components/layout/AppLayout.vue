<script setup>
import { defineAsyncComponent } from 'vue'

import { useAuthStore } from '@/stores/auth'

import AppFooter from './AppFooter.vue'
import AppHeader from './AppHeader.vue'

// Each theme's animated backdrop is downloaded only by users on that theme.
const SpaceBackdrop = defineAsyncComponent(() => import('./SpaceBackdrop.vue'))
const FloralBackdrop = defineAsyncComponent(() => import('./FloralBackdrop.vue'))
const NewsBackdrop = defineAsyncComponent(() => import('./NewsBackdrop.vue'))
const ForestBackdrop = defineAsyncComponent(() => import('./ForestBackdrop.vue'))
const AnimeBackdrop = defineAsyncComponent(() => import('./AnimeBackdrop.vue'))
const auth = useAuthStore()
</script>

<template>
  <div class="relative isolate flex min-h-screen flex-col">
    <!-- Theme backdrops behind the whole app: a live starfield with shooting stars on Space (ink),
         paper grain and flying newspaper planes on Newspaper, drawn flowers on Floral,
         a mountain meadow on Forest, a twilight sakura scene on Anime. -->
    <SpaceBackdrop v-if="auth.theme === 'ink'" />
    <div class="k-app-news" aria-hidden="true" />
    <FloralBackdrop v-if="auth.theme === 'floral'" />
    <NewsBackdrop v-if="auth.theme === 'news'" />
    <ForestBackdrop v-if="auth.theme === 'forest'" />
    <AnimeBackdrop v-if="auth.theme === 'anime'" />
    <a href="#main" class="k-label sr-only z-50 bg-accent px-4 py-2 text-on-accent focus:not-sr-only focus:fixed focus:top-2 focus:left-2">
      Skip to content
    </a>
    <AppHeader />
    <main id="main" class="flex-1">
      <!-- Pages rise in on navigation; the same page re-used with new params
           (another question, another conversation) doesn't re-animate. -->
      <RouterView v-slot="{ Component }">
        <Transition name="k-page">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <AppFooter />
  </div>
</template>
