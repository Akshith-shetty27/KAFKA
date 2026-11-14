/**
 * State and actions for one ASK KAFKA conversation, shared by the Ask KAFKA
 * page and the question-page drawer.
 *
 *   const chat = useChat({ ensureConversation })
 *   chat.send({ content, mode, hintLevel })
 *
 * `ensureConversation()` returns the conversation to post to, creating it on
 * the first message (so merely opening the drawer doesn't create empty
 * conversations).
 */
import { computed, ref, shallowRef } from 'vue'

import { assistantApi } from '@/services/assistant.api'
import { useAssistantStore } from '@/stores/assistant'

export function useChat({ ensureConversation }) {
  const store = useAssistantStore()
  const conversation = shallowRef(null)
  const messages = ref([])
  const streaming = ref(false)
  const error = ref(null) // { message, retryable }
  let controller = null
  let lastPayload = null

  function load(detail) {
    conversation.value = detail
    messages.value = detail ? [...detail.messages] : []
    error.value = null
  }

  /** Highest hint level already used in this conversation (0 if none). */
  const hintsUsed = computed(() =>
    messages.value.reduce((max, m) => (m.role === 'user' && m.mode === 'hint' ? Math.max(max, m.hint_level ?? 1) : max), 0),
  )

  async function send({ content, mode = 'chat', hintLevel = null }) {
    if (streaming.value || !content.trim()) return false
    error.value = null
    streaming.value = true
    lastPayload = { content, mode, hintLevel }
    controller = new AbortController()

    // Optimistic placeholder for the reply; filled token by token.
    const reply = ref({ id: `pending-${Date.now()}`, role: 'assistant', content: '', status: 'streaming' })
    let started = false

    try {
      const conv = await ensureConversation()
      if (!conversation.value) load(conv)
      await assistantApi.send(
        conv.id,
        { content: content.trim(), mode, ...(mode === 'hint' ? { hint_level: hintLevel ?? 1 } : {}) },
        {
          signal: controller.signal,
          onEvent(event) {
            if (event.type === 'start') {
              started = true
              messages.value.push(event.user_message, reply.value)
              // The server titles new conversations from their first message.
              if (event.conversation && conversation.value?.title !== event.conversation.title) {
                conversation.value = { ...conversation.value, title: event.conversation.title }
              }
            } else if (event.type === 'token') {
              reply.value.content += event.text
            } else if (event.type === 'done') {
              Object.assign(reply.value, event.message)
              store.touch(conversation.value, event.message)
            } else if (event.type === 'error') {
              if (event.saved) Object.assign(reply.value, event.saved)
              else messages.value = messages.value.filter((m) => m !== reply.value)
              error.value = { message: event.message, retryable: event.retryable }
            }
          },
        },
      )
      return true
    } catch (err) {
      if (err?.name === 'AbortError') {
        // Stopped by the student; the server keeps the partial reply.
        if (reply.value.content) reply.value.status = 'incomplete'
        else messages.value = messages.value.filter((m) => m !== reply.value)
        return true
      }
      if (started) {
        reply.value.status = 'error'
        error.value = { message: 'The connection dropped before KAFKA finished.', retryable: true }
      } else {
        error.value = { message: err?.message ?? 'Something went wrong.', retryable: err?.status !== 400, fields: err?.fields }
      }
      return false
    } finally {
      streaming.value = false
      controller = null
    }
  }

  function stop() {
    controller?.abort()
  }

  function retry() {
    if (lastPayload) send(lastPayload)
  }

  return { conversation, messages, streaming, error, hintsUsed, load, send, stop, retry }
}
