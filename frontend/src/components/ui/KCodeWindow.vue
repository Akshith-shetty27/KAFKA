<script setup>
/**
 * The tilted editor window from the hero panel: traffic lights, a path,
 * numbered lines and a status bar. `lines` is an array of token arrays:
 *   [[{ t: 'function', k: 'kw' }, { t: ' solve' , k: 'fn' }], …]
 * Token kinds: kw (keyword), fn (function), str (string), op, plain.
 */
defineProps({
  path: { type: String, default: 'kafka / practice' },
  lines: { type: Array, required: true },
  status: { type: String, default: '' },
  meta: { type: String, default: '' },
  tilt: { type: Boolean, default: true },
})

const tokenClass = {
  kw: 'text-teal-400',
  fn: 'text-paper-50 font-medium',
  str: 'text-[#f2b33d]',
  op: 'text-teal-400',
  plain: 'text-paper-50/85',
}
</script>

<template>
  <figure
    class="border border-ink-700 bg-ink-900 font-mono text-[13px] shadow-[0_30px_80px_-20px_rgb(0_0_0/0.8)] sm:text-sm"
    :class="tilt ? 'motion-safe:-rotate-2' : ''"
    data-surface="ink"
  >
    <div class="flex items-center gap-2 border-b border-ink-700 px-5 py-3.5">
      <span class="size-2.5 rounded-full bg-[#f0614a]" />
      <span class="size-2.5 rounded-full bg-[#f2b33d]" />
      <span class="size-2.5 rounded-full bg-teal-400" />
      <span class="mx-auto pr-10 text-xs tracking-wider text-paper-50/50">{{ path }}</span>
    </div>
    <pre class="overflow-x-auto px-5 py-5 leading-[2.1]"><code><span
      v-for="(line, i) in lines"
      :key="i"
      class="block"
    ><span class="mr-5 inline-block w-5 text-paper-50/30 select-none">{{ String(i + 1).padStart(2, '0') }}</span><span
      v-for="(tok, j) in line"
      :key="j"
      :class="tokenClass[tok.k ?? 'plain']"
    >{{ tok.t }}</span></span></code></pre>
    <figcaption
      v-if="status"
      class="flex items-center justify-between gap-4 border-t border-ink-700 bg-[#0f2a27] px-5 py-3 text-teal-400"
    >
      <span>✓ {{ status }}</span>
      <span v-if="meta" class="text-xs text-paper-50/45">{{ meta }}</span>
    </figcaption>
  </figure>
</template>
