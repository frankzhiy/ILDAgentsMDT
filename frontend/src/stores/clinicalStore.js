import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useClinicalStore = defineStore('clinical', () => {
  // Shared Board Data
  const rawCaseHistory = ref([])
  const structuredInfo = ref({})
  
  // Current Round Data
  const specialistOpinions = reactive({}) // { "Radiologist": "..." }
  const specialistSummaries = reactive({}) // { "Radiologist": "..." }
  const moderatorSummary = ref("")
  const conflicts = ref([]) // [{ issue: "...", severity: "high", ... }]
  const discussionNotes = ref("") // "Team Discussion Notes..."
  
  // History Data (Accumulated Rounds)
  const roundHistory = ref([])
  const currentRoundNumber = ref(0)
  
  // Internal Stream (for debugging)
  const internalStream = ref([])
  
  // Streaming buffer for structured info
  const streamingStructuredText = ref("")

  // Snapshot for Rollback
  const lastStableStructuredInfo = ref({})

  // Actions
  function startNewRound() {
    // Snapshot current structured info before starting new round
    lastStableStructuredInfo.value = JSON.parse(JSON.stringify(structuredInfo.value))

    // Only start a new round if the current one has data
    const hasData = Object.keys(specialistOpinions).length > 0 || moderatorSummary.value
    
    if (hasData) {
      // Archive current round
      roundHistory.value.push({
        round: currentRoundNumber.value,
        opinions: { ...specialistOpinions },
        summaries: { ...specialistSummaries },
        summary: moderatorSummary.value,
        conflicts: [...conflicts.value],
        discussionNotes: discussionNotes.value
      })
      
      // Reset current round data
      Object.keys(specialistOpinions).forEach(key => delete specialistOpinions[key])
      Object.keys(specialistSummaries).forEach(key => delete specialistSummaries[key])
      moderatorSummary.value = ""
      conflicts.value = []
      discussionNotes.value = ""
      
      // Increment round number
      currentRoundNumber.value += 1
    }
  }

  function rollbackCurrentRound() {
    // Restore structured info
    structuredInfo.value = JSON.parse(JSON.stringify(lastStableStructuredInfo.value))
    
    // Clear current round data (effectively cancelling the round)
    Object.keys(specialistOpinions).forEach(key => delete specialistOpinions[key])
    Object.keys(specialistSummaries).forEach(key => delete specialistSummaries[key])
    moderatorSummary.value = ""
    conflicts.value = []
    discussionNotes.value = ""
    streamingStructuredText.value = ""
  }

  function updateStructuredInfo(info) {
    structuredInfo.value = info
  }
  
  function setConflicts(newConflicts) {
    conflicts.value = newConflicts
  }

  function setDiscussionNotes(notes) {
    discussionNotes.value = notes
  }

  function appendDiscussionNotes(content) {
    discussionNotes.value += content
  }

  function appendStreamingStructuredText(content) {
    streamingStructuredText.value += content
  }

  function clearStreamingStructuredText() {
    streamingStructuredText.value = ""
  }

  function appendSpecialistOpinion(role, content) {
    if (!specialistOpinions[role]) {
      specialistOpinions[role] = ""
    }
    specialistOpinions[role] += content
  }

  function setSpecialistOpinion(role, content) {
    specialistOpinions[role] = content
  }

  function appendSpecialistSummary(role, content) {
    if (!specialistSummaries[role]) {
      specialistSummaries[role] = ""
    }
    specialistSummaries[role] += content
  }

  function setSpecialistSummary(role, content) {
    specialistSummaries[role] = content
  }

  function appendModeratorSummary(content) {
    moderatorSummary.value += content
  }

  function setModeratorSummary(content) {
    moderatorSummary.value = content
  }

  return {
    rawCaseHistory,
    structuredInfo,
    specialistOpinions,
    specialistSummaries,
    moderatorSummary,
    conflicts,
    discussionNotes,
    roundHistory,
    currentRoundNumber,
    internalStream,
    streamingStructuredText,
    startNewRound,
    rollbackCurrentRound,
    updateStructuredInfo,
    appendStreamingStructuredText,
    clearStreamingStructuredText,
    appendSpecialistOpinion,
    setSpecialistOpinion,
    appendSpecialistSummary,
    setSpecialistSummary,
    appendModeratorSummary,
    setModeratorSummary,
    setDiscussionNotes,
    appendDiscussionNotes,
    setConflicts,
    conflicts
  }
})
