import axios from 'axios'
import { useConnectionStore } from '../stores/connectionStore'
import { useChatStore } from '../stores/chatStore'
import { useClinicalStore } from '../stores/clinicalStore'

const api = axios.create({
  baseURL: '/api'
})

let websocket = null

export const mdtApi = {
  async createSession() {
    const response = await api.post('/sessions')
    return response.data.session_id
  },

  async submitCase(sessionId, caseText, selectedAgents, modelConfigs) {
    return await api.post(`/sessions/${sessionId}/case`, {
      case_text: caseText,
      selected_agents: selectedAgents,
      model_configs: modelConfigs
    })
  },

  connectWebSocket(sessionId, config) {
    const connectionStore = useConnectionStore()
    
    if (websocket) {
      websocket.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/consultation/${sessionId}`
    
    websocket = new WebSocket(wsUrl)

    websocket.onopen = () => {
      connectionStore.isConnected = true
      connectionStore.addLog("WebSocket Connected")
      // Send configuration to start the round
      websocket.send(JSON.stringify(config))
      connectionStore.isRunning = true
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleEvent(data)
    }

    websocket.onclose = () => {
      connectionStore.isConnected = false
      connectionStore.isRunning = false
      connectionStore.addLog("WebSocket Disconnected")
    }

    websocket.onerror = (error) => {
      connectionStore.addLog(`WebSocket Error: ${error}`)
    }
  },

  stopSession() {
    if (websocket) {
      websocket.close()
      websocket = null
      const connectionStore = useConnectionStore()
      const clinicalStore = useClinicalStore()
      
      clinicalStore.rollbackCurrentRound()
      connectionStore.stopGeneration()
      connectionStore.addLog("Session Stopped by User (Rolled Back)")
    }
  }
}

function handleEvent(data) {
  const connectionStore = useConnectionStore()
  const chatStore = useChatStore()
  const clinicalStore = useClinicalStore()

  switch (data.type) {
    case 'status':
      connectionStore.updateAgentStatus(data.role, data.content)
      // Clear streaming buffer when Organizer starts working
      if (data.role === 'Case Organizer' && data.content === 'working') {
        clinicalStore.clearStreamingStructuredText()
        clinicalStore.updateStructuredInfo({})
      }
      // Clear specialist opinion when they start working
      if (data.content === 'working') {
        clinicalStore.setSpecialistOpinion(data.role, "")
        clinicalStore.setSpecialistSummary(data.role, "")
      }
      break
      
    case 'token':
      // Stream content to appropriate destination
      const { role, content, target } = data
      
      if (role === 'Moderator') {
        if (target === 'summary') {
          // Stream to InfoPanel (Final Conclusion)
          clinicalStore.appendModeratorSummary(content)
        } else {
          // Stream to ChatPanel (Patient Reply)
          const lastMsg = chatStore.chatHistory[chatStore.chatHistory.length - 1]
          if (lastMsg && lastMsg.role === 'Moderator') {
            chatStore.appendToLastMessage(content)
          } else {
            chatStore.addChatMessage('Moderator', content, '')
          }
        }
      } else if (role === 'Case Organizer') {
         clinicalStore.appendStreamingStructuredText(content)
      } else if (role === 'Team Discussion') {
         clinicalStore.appendDiscussionNotes(content)
      } else {
        // Specialists
        if (target === 'specialist_summary') {
          clinicalStore.appendSpecialistSummary(role, content)
        } else {
          // Default to opinions
          clinicalStore.appendSpecialistOpinion(role, content)
        }
      }
      
      // Also keep internal stream for debugging
      clinicalStore.internalStream.push(`[${data.role}] ${data.content}`)
      break
      
    case 'node_finished':
      // Update structured data
      const output = data.data
      if (output.structured_info) {
        clinicalStore.updateStructuredInfo(output.structured_info)
        // Clear streaming text as we have the final object
        clinicalStore.clearStreamingStructuredText()
      }
      if (output.specialist_opinions) {
        // We might have already streamed it, but this ensures consistency
        Object.entries(output.specialist_opinions).forEach(([role, content]) => {
            clinicalStore.setSpecialistOpinion(role, content)
        })
      }
      if (output.specialist_summaries) {
        Object.entries(output.specialist_summaries).forEach(([role, content]) => {
            clinicalStore.setSpecialistSummary(role, content)
        })
      }
      if (output.moderator_summary) {
        clinicalStore.setModeratorSummary(output.moderator_summary)
      }
      if (output.conflicts) {
        clinicalStore.setConflicts(output.conflicts)
      }
      if (output.discussion_notes) {
        clinicalStore.setDiscussionNotes(output.discussion_notes)
      }
      if (output.chat_history) {
        // Only add to chat history if it's NOT a specialist opinion (which are internal)
        // Moderator messages should be in chat history.
        // User messages are already there.
        // Specialists are filtered out from chat.
        output.chat_history.forEach(msg => {
          if (msg.role === 'Moderator') {
             // Update the last message (which was streaming) with final content and model
             const lastMsg = chatStore.chatHistory[chatStore.chatHistory.length - 1]
             if (lastMsg && lastMsg.role === 'Moderator') {
               lastMsg.content = msg.content
               lastMsg.model = msg.model
             } else {
               chatStore.addChatMessage(msg.role, msg.content, msg.model)
             }
          }
          // Ignore other roles for chat window
        })
      }
      break
      
    case 'log':
      connectionStore.addLog(data.content)
      break
      
    case 'done':
      connectionStore.isRunning = false
      connectionStore.addLog("Consultation Round Finished")
      break
      
    case 'error':
      connectionStore.addLog(`Error: ${data.content}`)
      connectionStore.isRunning = false
      break
  }
}
