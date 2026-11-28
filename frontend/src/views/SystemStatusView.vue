<script setup>
import { computed, onMounted } from 'vue'

import { useAsync } from '@/composables/useAsync'
import { systemApi } from '@/services/system.api'

const { data, error, loading, run } = useAsync(() => systemApi.health())

const rows = computed(() => [
  { label: 'Frontend', value: 'ok' },
  { label: 'API', value: loading.value ? 'checking' : error.value ? 'down' : 'ok' },
  { label: 'Database', value: loading.value ? 'checking' : data.value?.database ?? 'unknown' },
])

onMounted(run)
</script>

<template>
  <main data-surface="ink" class="min-h-screen bg-[var(--k-bg)] px-4 py-16 text-[var(--k-text)] sm:px-12">
    <div class="mx-auto max-w-3xl">
      <p class="font-mono text-xs tracking-[0.3em] text-[var(--k-text-muted)] uppercase">System status</p>

      <h1 class="font-display mt-8 text-5xl leading-[0.9] font-semibold tracking-[-0.04em] uppercase sm:text-7xl">
        Kafka&nbsp;<span class="font-serif font-normal tracking-normal normal-case italic">is</span>&nbsp;<span :class="error ? 'text-signal-red' : 'text-teal-400'">{{ error ? 'offline.' : 'online.' }}</span>
      </h1>

      <ul class="mt-12 border-t border-[var(--k-rule)]">
        <li
          v-for="row in rows"
          :key="row.label"
          class="flex items-center justify-between border-b border-[var(--k-rule)] py-4 font-mono text-sm"
        >
          <span class="flex items-center gap-3">
            <span
              class="size-3"
              :class="{
                'bg-teal-400': row.value === 'ok',
                'bg-signal-red': row.value === 'down',
                'border border-[var(--k-text-muted)]': !['ok', 'down'].includes(row.value),
              }"
            />
            {{ row.label }}
          </span>
          <span class="tracking-[0.2em] text-[var(--k-text-muted)] uppercase">{{ row.value }}</span>
        </li>
      </ul>

      <p v-if="error" class="mt-6 font-mono text-sm text-signal-red">{{ error.message }}</p>

      <button
        type="button"
        class="mt-10 border-b border-current pb-1 font-sans text-sm tracking-[0.25em] uppercase transition-colors hover:text-teal-400 disabled:opacity-50"
        :disabled="loading"
        @click="run"
      >
        Check again ↻
      </button>
    </div>
  </main>
</template>
