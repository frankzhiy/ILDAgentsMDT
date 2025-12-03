<template>
  <div class="h-full flex flex-col bg-white border-r border-gray-200">
    <div class="p-4 border-b border-gray-200">
      <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
        <el-icon><Setting /></el-icon>
        配置面板
      </h2>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-6">
      <!-- Agent Selection -->
      <div>
        <h3 class="text-sm font-semibold text-gray-600 mb-3">参与专家</h3>
        <div class="space-y-2">
          <div v-for="agent in agents" :key="agent.key" class="flex items-center">
            <el-checkbox v-model="selectedAgents" :label="agent.key">
              <span class="text-gray-700">{{ agent.label }}</span>
            </el-checkbox>
          </div>
        </div>
      </div>

      <el-divider />

      <!-- Model Configuration -->
      <div>
        <h3 class="text-sm font-semibold text-gray-600 mb-3">模型配置</h3>
        <el-radio-group v-model="configMode" size="small" class="mb-4">
          <el-radio-button label="global">统一配置</el-radio-button>
          <el-radio-button label="custom">单独配置</el-radio-button>
        </el-radio-group>

        <div v-if="configMode === 'global'" class="space-y-4">
          <div>
            <label class="text-xs text-gray-500 block mb-1">统一模型</label>
            <el-select v-model="globalModel" placeholder="Select">
              <el-option v-for="opt in modelOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div v-for="agent in activeAgents" :key="agent.key" class="border-l-2 border-blue-500 pl-3">
            <label class="text-xs text-gray-500 block mb-1">{{ agent.label }}</label>
            <el-select v-model="agentConfigs[agent.key]" size="small">
              <el-option v-for="opt in modelOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useConnectionStore } from '../stores/connectionStore'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue', 'config-change'])

const connectionStore = useConnectionStore()
// No need to destructure storeToRefs for simple usage if we don't need reactivity on the store object itself, 
// but for state properties we usually want storeToRefs or just access via store.prop
// Here we just use it to check status.

const agents = [
  { key: "Case Organizer", label: "📋 病例整理员" },
  { key: "Radiologist", label: "☢️ 影像科医生" },
  { key: "Pathologist", label: "🔬 病理科医生" },
  { key: "Pulmonologist", label: "🫁 呼吸科医生" },
  { key: "Rheumatologist", label: "🦴 风湿科医生" },
  { key: "Conflict Detector", label: "⚖️ 冲突检测员" },
  { key: "Team Discussion", label: "💬 团队讨论" },
  { key: "Moderator", label: "👨‍🏫 主持专家" }
]

const modelOptions = [
  { label: "GPT-5.1", value: "gpt-5.1" },
  { label: "DeepSeek V3", value: "deepseek-v3-2-exp" },
  { label: "Claude Haiku", value: "claude-haiku-4-5-20251001" },
  { label: "Gemini 2.5 Pro", value: "gemini-2.5-pro" },
  { label: "Grok 4", value: "grok-4" },
  { label: "Qwen 3", value: "qwen3-235b-a22b" }
]

const selectedAgents = ref(agents.map(a => a.key))
const configMode = ref('global')
const globalModel = ref('deepseek-v3-2-exp')
const agentConfigs = ref({})

// Initialize default configs
agents.forEach(a => agentConfigs.value[a.key] = 'deepseek-v3-2-exp')

// Load from localStorage
const STORAGE_KEY = 'mdt_config_v1'
try {
  const savedConfig = localStorage.getItem(STORAGE_KEY)
  if (savedConfig) {
    const parsed = JSON.parse(savedConfig)
    if (parsed.selectedAgents) selectedAgents.value = parsed.selectedAgents
    if (parsed.configMode) configMode.value = parsed.configMode
    if (parsed.globalModel) globalModel.value = parsed.globalModel
    if (parsed.agentConfigs) {
      // Merge saved configs with defaults to handle potential new agents
      agentConfigs.value = { ...agentConfigs.value, ...parsed.agentConfigs }
    }
  }
} catch (e) {
  console.error('Failed to load config from localStorage', e)
}

const activeAgents = computed(() => {
  return agents.filter(a => selectedAgents.value.includes(a.key))
})

// Watch changes and emit configuration
watch([selectedAgents, configMode, globalModel, agentConfigs], () => {
  // Save to localStorage
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      selectedAgents: selectedAgents.value,
      configMode: configMode.value,
      globalModel: globalModel.value,
      agentConfigs: agentConfigs.value
    }))
  } catch (e) {
    console.error('Failed to save config to localStorage', e)
  }

  const configs = {}
  if (configMode.value === 'global') {
    selectedAgents.value.forEach(key => {
      configs[key] = globalModel.value
    })
  } else {
    selectedAgents.value.forEach(key => {
      configs[key] = agentConfigs.value[key]
    })
  }
  
  // Update store status for unselected agents
  agents.forEach(agent => {
    if (!selectedAgents.value.includes(agent.key)) {
      connectionStore.updateAgentStatus(agent.key, 'offline')
    } else {
      // If coming back online, set to idle
      if (connectionStore.agentStatus[agent.key] === 'offline') {
        connectionStore.updateAgentStatus(agent.key, 'idle')
      }
    }
  })

  emit('config-change', {
    selectedAgents: selectedAgents.value,
    modelConfigs: configs
  })
}, { deep: true, immediate: true })
</script>
