<script setup>
defineProps({
  lines: { type: Number, default: 3 },
  height: { type: String, default: '1rem' },
})
</script>

<template>
  <div class="flex flex-col gap-3" aria-hidden="true">
    <span
      v-for="n in lines"
      :key="n"
      class="block animate-pulse bg-rule-soft"
      :style="{ height, width: n === lines && lines > 1 ? '60%' : '100%' }"
    />
  </div>
</template>
