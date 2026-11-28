<template>
  <main class="flex min-h-screen flex-col justify-center px-4 sm:px-12">
    <p class="font-mono text-xs tracking-[0.3em] text-[var(--k-text-muted)] uppercase">Error 404</p>
    <h1 class="font-display mt-6 text-6xl leading-[0.9] font-semibold tracking-[-0.04em] uppercase sm:text-8xl">
      Page&nbsp;<span class="font-serif font-normal tracking-normal normal-case italic">not</span>&nbsp;found.
    </h1>
    <RouterLink
      to="/"
      class="mt-10 self-start border-b border-current pb-1 text-sm tracking-[0.25em] uppercase hover:text-teal-500"
    >
      Back home ↗
    </RouterLink>
  </main>
</template>
