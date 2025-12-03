import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useConnectionStore = defineStore('connection', () => {
  // State
  const sessionId = ref(null)
  const isConnected = ref(false)
  const isRunning = ref(false)
  
  // Agent Status: { "Radiologist": "idle" | "working" | "offline" }
  const agentStatus = reactive({
    "Case Organizer": "idle",
    "Radiologist": "idle",
    "Pathologist": "idle",
    "Pulmonologist": "idle",
    "Rheumatologist": "idle",
    "Conflict Detector": "idle",
    "Team Discussion": "idle",
    "Moderator": "idle"
  })

  const executionLogs = ref([])

  // Actions
  function setSessionId(id) {
    sessionId.value = id
  }

  function updateAgentStatus(role, status) {
    if (agentStatus[role] !== undefined) {
      agentStatus[role] = status
    }
  }

  function resetAgentStatuses() {
    Object.keys(agentStatus).forEach(key => agentStatus[key] = 'idle')
  }

  function addLog(content) {
    executionLogs.value.push(`[${new Date().toLocaleTimeString()}] ${content}`)
  }

  function stopGeneration() {
    isRunning.value = false
    resetAgentStatuses()
  }

  return {
    sessionId,
    isConnected,
    isRunning,
    agentStatus,
    executionLogs,
    setSessionId,
    updateAgentStatus,
    resetAgentStatuses,
    addLog,
    stopGeneration
  }
})
