<script setup>
/**
 * Renders the toasts from useToast(). Polite announcements for success/info,
 * assertive for errors; each toast can be closed with its button (keyboard
 * reachable) and pauses while hovered or focused.
 */
import KIcon from '@/components/ui/KIcon.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const icon = { success: 'check', error: 'alert', info: 'arrow-right' }
</script>

<template>
  <div class="pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-center gap-2 sm:inset-x-auto sm:right-6 sm:bottom-6 sm:items-end">
    <div class="sr-only" aria-live="polite">
      <template v-for="t in toast.items" :key="t.id"><span v-if="t.kind !== 'error'">{{ t.message }}</span></template>
    </div>
    <div class="sr-only" aria-live="assertive">
      <template v-for="t in toast.items" :key="t.id"><span v-if="t.kind === 'error'">{{ t.message }}</span></template>
    </div>
    <TransitionGroup
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-3 opacity-0"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="translate-y-2 opacity-0"
      move-class="transition duration-300"
    >
      <div
        v-for="t in toast.items"
        :key="t.id"
        data-surface="ink"
        class="pointer-events-auto flex w-full max-w-sm items-start gap-3 border border-rule px-4 py-3 shadow-elevated sm:w-96"
        @mouseenter="toast.pause(t.id)"
        @mouseleave="toast.resume(t.id)"
        @focusin="toast.pause(t.id)"
        @focusout="toast.resume(t.id)"
      >
        <span
          class="mt-0.5 flex size-5 shrink-0 items-center justify-center"
          :class="t.kind === 'error' ? 'text-danger' : 'text-accent'"
          aria-hidden="true"
        >
          <KIcon :name="icon[t.kind]" :size="16" />
        </span>
        <p class="min-w-0 flex-1 text-sm leading-relaxed">{{ t.message }}</p>
        <button
          type="button"
          class="-mr-1 flex size-6 shrink-0 items-center justify-center text-muted hover:text-fg"
          aria-label="Dismiss notification"
          @click="toast.dismiss(t.id)"
        >
          <KIcon name="x" :size="14" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
