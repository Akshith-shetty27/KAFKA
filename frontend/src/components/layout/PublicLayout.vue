<script setup>
import PublicHeader from './PublicHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <a href="#main" class="k-label sr-only z-50 bg-accent px-4 py-2 text-on-accent focus:not-sr-only focus:fixed focus:top-2 focus:left-2">
      Skip to content
    </a>
    <PublicHeader />
    <main id="main" class="flex-1">
      <RouterView />
    </main>
  </div>
</template>
