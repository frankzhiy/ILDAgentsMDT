import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // State
  const chatHistory = ref([])

  // Actions
  function addChatMessage(role, content, model = "") {
    chatHistory.value.push({ role, content, model })
  }

  function appendToLastMessage(content) {
    if (chatHistory.value.length > 0) {
      const lastMsg = chatHistory.value[chatHistory.value.length - 1]
      lastMsg.content += content
    }
  }

  return {
    chatHistory,
    addChatMessage,
    appendToLastMessage
  }
})
