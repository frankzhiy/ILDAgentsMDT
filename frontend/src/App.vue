<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-gray-100">
    <!-- Header -->
    <Header class="flex-none h-16" />

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Sidebar -->
      <Sidebar 
        class="w-64 flex-none hidden md:flex" 
        @config-change="handleConfigChange"
      />

      <!-- Split View -->
      <div class="flex-1 flex">
        <!-- Chat Panel (Left) -->
        <div class="flex-1 flex flex-col min-w-0 border-r border-gray-200">
          <ChatPanel @submit="handleSubmit" />
        </div>

        <!-- Info Panel (Right) -->
        <div class="w-[450px] flex-none hidden lg:flex flex-col bg-white">
          <InfoPanel />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import ChatPanel from './components/ChatPanel.vue'
import InfoPanel from './components/InfoPanel.vue'
import { mdtApi } from './api/client'
import { useConnectionStore } from './stores/connectionStore'
import { useChatStore } from './stores/chatStore'
import { ElMessage } from 'element-plus'

const connectionStore = useConnectionStore()
const chatStore = useChatStore()

const currentConfig = ref({
  selectedAgents: [],
  modelConfigs: {}
})

onMounted(async () => {
  try {
    const sessionId = await mdtApi.createSession()
    connectionStore.setSessionId(sessionId)
    connectionStore.addLog(`Session Created: ${sessionId}`)
  } catch (e) {
    ElMessage.error('Failed to connect to backend server.')
    connectionStore.addLog(`Error creating session: ${e}`)
  }
})

function handleConfigChange(config) {
  currentConfig.value = config
}

async function handleSubmit(text) {
  if (!connectionStore.sessionId) {
    ElMessage.warning('Session not initialized yet.')
    return
  }

  // Add user message to chat immediately
  chatStore.addChatMessage('user', text)

  try {
    // 1. Submit Case via HTTP
    await mdtApi.submitCase(
      connectionStore.sessionId, 
      text, 
      currentConfig.value.selectedAgents, 
      currentConfig.value.modelConfigs
    )

    // 2. Connect WebSocket to start the round
    mdtApi.connectWebSocket(connectionStore.sessionId, {
      selected_agents: currentConfig.value.selectedAgents,
      model_configs: currentConfig.value.modelConfigs
    })
    
  } catch (e) {
    ElMessage.error('Failed to submit case.')
    connectionStore.addLog(`Error submitting case: ${e}`)
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Inter', sans-serif;
}
</style>
