<script setup>
/**
 * "TODAY'S PLAN" rows: square marker, mono label, DONE/NEXT tag, hairlines.
 * items: [{ key, label, meta?, done, tag?, to? }]
 */
defineProps({
  items: { type: Array, required: true },
  title: { type: String, default: '' },
})
</script>

<template>
  <div>
    <p v-if="title" class="k-eyebrow mb-5 text-muted">{{ title }}</p>
    <ul class="border-t border-rule">
      <li v-for="item in items" :key="item.key" class="border-b border-rule">
        <component
          :is="item.to ? 'RouterLink' : 'div'"
          :to="item.to"
          class="flex items-center gap-4 py-4"
          :class="item.to ? 'transition-colors hover:text-accent-text' : ''"
        >
          <span
            class="size-[18px] shrink-0"
            :class="item.done ? 'bg-accent' : 'border-[1.5px] border-fg'"
            :aria-label="item.done ? 'Done' : 'Not done'"
            role="img"
          />
          <span class="min-w-0 flex-1">
            <span class="block truncate font-mono text-[15px]">{{ item.label }}</span>
            <span v-if="item.meta" class="mt-1 block truncate text-sm text-muted">{{ item.meta }}</span>
          </span>
          <span class="k-eyebrow shrink-0 text-muted">{{ item.tag ?? (item.done ? 'Done' : '') }}</span>
        </component>
      </li>
    </ul>
  </div>
</template>
