<script setup>
import AppFooter from './AppFooter.vue'
import AppHeader from './AppHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col">
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
