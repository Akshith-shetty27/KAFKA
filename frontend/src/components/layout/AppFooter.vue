<script setup>
const year = new Date().getFullYear()
</script>

<template>
  <footer class="border-t border-rule-soft">
    <div class="k-container flex flex-col gap-4 py-8 sm:flex-row sm:items-center sm:justify-between">
      <span class="k-display text-xl tracking-[-0.06em]">KAFKA<span class="text-accent">.</span></span>
      <p class="k-eyebrow text-muted">Interview preparation · {{ year }}</p>
    </div>
  </footer>
</template>
