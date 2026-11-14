/**
 * ASK KAFKA app-wide state: which provider is answering (to show the offline
 * demo badge) and the conversation list shown on the Ask KAFKA page.
 * The messages of an open conversation live in the `useChat` composable.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { assistantApi } from '@/services/assistant.api'

export const useAssistantStore = defineStore('assistant', () => {
  const status = ref(null)
  const conversations = ref([])
  const loadingList = ref(false)
  const listError = ref(null)

  async function loadStatus() {
    if (status.value) return status.value
    try {
      status.value = await assistantApi.status()
    } catch {
      status.value = null
    }
    return status.value
  }

  async function loadConversations() {
    loadingList.value = true
    listError.value = null
    try {
      conversations.value = (await assistantApi.list({ page_size: 50 })).results
    } catch (err) {
      listError.value = err.apiError ?? { message: 'Could not load conversations.' }
    } finally {
      loadingList.value = false
    }
  }

  /** Keep the list fresh after a message without refetching everything. */
  function touch(conversation, lastMessage) {
    const rest = conversations.value.filter((c) => c.id !== conversation.id)
    conversations.value = [
      {
        id: conversation.id,
        title: conversation.title,
        question: conversation.question,
        updated_at: new Date().toISOString(),
        last_message: lastMessage ? { role: lastMessage.role, preview: lastMessage.content.slice(0, 140) } : null,
      },
      ...rest,
    ]
  }

  async function remove(id) {
    await assistantApi.remove(id)
    conversations.value = conversations.value.filter((c) => c.id !== id)
  }

  return { status, conversations, loadingList, listError, loadStatus, loadConversations, touch, remove }
})
