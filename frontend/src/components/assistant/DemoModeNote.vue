<script setup>
import { onMounted } from 'vue'

import { useAssistantStore } from '@/stores/assistant'

const store = useAssistantStore()
onMounted(store.loadStatus)
</script>

<template>
  <p v-if="store.status?.offline" class="border-l-2 border-warning pl-3 text-xs leading-relaxed text-muted" role="note">
    <strong class="font-medium text-fg">Offline demo mode.</strong>
    Replies are placeholders until the server is switched to Groq (<code>LLM_PROVIDER=groq</code>).
  </p>
  <p v-else-if="store.status && !store.status.configured" class="border-l-2 border-warning pl-3 text-xs leading-relaxed text-muted" role="note">
    <strong class="font-medium text-fg">ASK KAFKA isn't set up yet.</strong>
    The server needs a <code>GROQ_API_KEY</code> before KAFKA can answer.
  </p>
</template>
