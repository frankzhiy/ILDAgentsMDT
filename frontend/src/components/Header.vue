<template>
  <div class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm z-10">
    <div class="flex items-center gap-3">
      <div class="bg-blue-600 text-white p-2 rounded-lg">
        <el-icon :size="20"><Monitor /></el-icon>
      </div>
      <div>
        <h1 class="text-lg font-bold text-gray-800 leading-tight">ILD Agents MDT</h1>
        <p class="text-xs text-gray-500">多智能体间质性肺病会诊系统</p>
      </div>
    </div>

    <!-- Agent Status Monitor -->
    <div class="flex items-center gap-6">
      <!-- Tools Group -->
      <div class="flex items-center gap-3 border-r border-gray-200 pr-6">
        <div 
          v-for="agent in toolAgents" 
          :key="agent.key"
          class="flex flex-col items-center transition-all duration-300"
          :class="{'opacity-40': getStatus(agent.key) === 'offline'}"
        >
          <div 
            class="w-10 h-10 rounded-full flex items-center justify-center text-xl border-2 bg-gray-50 relative"
            :class="getStatusClass(agent.key)"
          >
            {{ agent.icon }}
            <div 
              v-if="getStatus(agent.key) === 'working'"
              class="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"
            ></div>
          </div>
          <span class="text-[10px] mt-1 font-medium text-gray-500">{{ agent.shortName }}</span>
        </div>
      </div>

      <!-- Doctors Group -->
      <div class="flex items-center gap-3">
        <div 
          v-for="agent in doctorAgents" 
          :key="agent.key"
          class="flex flex-col items-center transition-all duration-300"
          :class="{'opacity-40': getStatus(agent.key) === 'offline'}"
        >
          <div 
            class="w-10 h-10 rounded-full flex items-center justify-center text-xl border-2 bg-white relative"
            :class="getStatusClass(agent.key)"
          >
            {{ agent.icon }}
            <div 
              v-if="getStatus(agent.key) === 'working'"
              class="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"
            ></div>
          </div>
          <span class="text-[10px] mt-1 font-medium text-gray-600">{{ agent.shortName }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useConnectionStore } from '../stores/connectionStore'
import { storeToRefs } from 'pinia'

const store = useConnectionStore()
const { agentStatus } = storeToRefs(store)

const toolAgents = [
  { key: "Case Organizer", icon: "📋", shortName: "整理" },
  { key: "Conflict Detector", icon: "⚖️", shortName: "冲突" },
  { key: "Team Discussion", icon: "💬", shortName: "讨论" }
]

const doctorAgents = [
  { key: "Radiologist", icon: "☢️", shortName: "影像" },
  { key: "Pathologist", icon: "🔬", shortName: "病理" },
  { key: "Pulmonologist", icon: "🫁", shortName: "呼吸" },
  { key: "Rheumatologist", icon: "🦴", shortName: "风湿" },
  { key: "Moderator", icon: "👨‍🏫", shortName: "主持" }
]

function getStatus(role) {
  return agentStatus.value[role] || 'offline'
}

function getStatusClass(role) {
  const status = getStatus(role)
  if (status === 'working') {
    return 'border-blue-500 text-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.5)] animate-pulse'
  } else if (status === 'idle') {
    return 'border-gray-200 text-gray-600'
  } else {
    return 'border-gray-100 text-gray-300'
  }
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 rgba(59, 130, 246, 0); }
  50% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); border-color: #3b82f6; }
}
.animate-pulse {
  animation: pulse 2s infinite;
}
</style>
