<script setup>
/**
 * Full-screen Ink menu for small screens: large display-type links.
 * Closes on route change and on Escape; focus moves into the menu.
 */
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import KIcon from '@/components/ui/KIcon.vue'

defineProps({
  items: { type: Array, required: true }, // [{ label, to }]
})

const open = ref(false)
const openButton = ref(null)
const closeButton = ref(null)
const route = useRoute()
let navigated = false

watch(
  () => route.fullPath,
  () => {
    navigated = open.value
    open.value = false
  },
)
watch(open, async (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
  if (isOpen) {
    await nextTick()
    closeButton.value?.focus()
  } else if (!navigated) {
    // Closed without navigating (× or Escape): return focus to the menu button.
    openButton.value?.focus()
  }
  navigated = false
})

function onKey(event) {
  if (event.key === 'Escape') open.value = false
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="lg:hidden">
    <button
      ref="openButton"
      type="button"
      class="-mr-2 flex size-11 items-center justify-center text-fg"
      aria-label="Open menu"
      :aria-expanded="open"
      @click="open = true"
    >
      <KIcon name="menu" :size="24" />
    </button>

    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        leave-active-class="transition-opacity duration-150"
        enter-from-class="opacity-0"
        leave-to-class="opacity-0"
      >
        <div
          v-if="open"
          data-surface="ink"
          class="k-grid fixed inset-0 z-50 flex flex-col px-4 pt-5 pb-10 sm:px-8"
          role="dialog"
          aria-modal="true"
          aria-label="Menu"
        >
          <div class="flex items-center justify-between">
            <span class="k-display text-[1.75rem] tracking-[-0.06em]">KAFKA<span class="text-accent">.</span></span>
            <button
              ref="closeButton"
              type="button"
              class="-mr-2 flex size-11 items-center justify-center"
              aria-label="Close menu"
              @click="open = false"
            >
              <KIcon name="close" :size="24" />
            </button>
          </div>
          <nav class="mt-14 flex flex-col" aria-label="Mobile">
            <RouterLink
              v-for="(item, i) in items"
              :key="item.label"
              :to="item.to"
              class="k-display k-rise border-b border-rule py-4 text-[2.75rem] hover:text-accent"
              :style="{ '--i': i }"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
          <div class="mt-auto">
            <slot name="footer" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
