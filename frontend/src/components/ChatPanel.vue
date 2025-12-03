<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Chat History -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
      <div v-if="chatHistory.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
        <el-icon :size="48" class="mb-2"><ChatDotRound /></el-icon>
        <p>请输入病例信息开始会诊...</p>
      </div>

      <div v-for="(msg, index) in chatHistory" :key="index" class="flex flex-col gap-1">
        <!-- Role Label -->
        <div class="flex items-center gap-2 px-2">
          <span class="text-xs font-bold text-gray-500" :class="{'text-blue-600': msg.role === 'user'}">
            {{ msg.role === 'user' ? '👤 患者/医生' : `👨‍⚕️ ${msg.role}` }}
          </span>
          <span v-if="msg.model" class="text-[10px] bg-gray-200 px-1 rounded text-gray-500">{{ msg.model }}</span>
        </div>
        
        <!-- Message Bubble -->
        <div 
          class="p-3 rounded-lg text-sm leading-relaxed shadow-sm max-w-[90%]"
          :class="msg.role === 'user' ? 'bg-blue-50 border border-blue-100 self-end' : 'bg-white border border-gray-200 self-start'"
        >
          <div v-if="msg.role === 'user'">{{ msg.content }}</div>
          <div v-else v-html="renderMarkdown(msg.content)" class="markdown-body"></div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 bg-white border-t border-gray-200">
      <div class="flex gap-2">
        <el-input
          v-model="input"
          type="textarea"
          :rows="3"
          placeholder="描述患者症状、检查结果..."
          resize="none"
          @keydown.enter.ctrl="sendMessage"
        />
        <div class="flex flex-col gap-2">
          <el-button 
            v-if="!isRunning"
            type="primary" 
            class="h-full w-24" 
            :disabled="!input.trim()" 
            @click="sendMessage"
          >
            发送
          </el-button>
          <el-button 
            v-else
            type="danger" 
            class="h-full w-24" 
            @click="stopGeneration"
          >
            停止
          </el-button>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="mt-2 flex gap-2">
        <el-select v-model="selectedCase" placeholder="选择测试病例" size="small" @change="fillCase">
          <el-option label="测试病例 1 (典型 ILD)" value="case1" />
          <el-option label="测试病例 2 (补充检查)" value="case2" />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chatStore'
import { useConnectionStore } from '../stores/connectionStore'
import { useClinicalStore } from '../stores/clinicalStore'
import { storeToRefs } from 'pinia'
import MarkdownIt from 'markdown-it'
import { mdtApi } from '../api/client'

const md = new MarkdownIt()
const chatStore = useChatStore()
const connectionStore = useConnectionStore()
const clinicalStore = useClinicalStore()

const { chatHistory } = storeToRefs(chatStore)
const { isRunning } = storeToRefs(connectionStore)
const emit = defineEmits(['submit'])

const input = ref('')
const chatContainer = ref(null)
const selectedCase = ref('')

const TEST_CASES = {
  case1: "患者女性，52 岁，办公室文员，非吸烟者。自述约半年多前开始出现活动后气促，最初在快走或上楼时偶有胸闷感，近两三个月气促逐渐加重，伴少量干咳。HRCT显示双肺散在片状影及多发网状影。",
  case2: "补充肺功能检查：FVC 1.98 L (68%)，FEV1 1.72 L (72%)，DLCO 47%。免疫学检查 ANA 1:320 阳性。"
}

function fillCase(val) {
  if (TEST_CASES[val]) {
    input.value = TEST_CASES[val]
  }
}

function sendMessage() {
  if (!input.value.trim()) return
  
  // If we are sending a new message, it means a new round starts
  clinicalStore.startNewRound()
  
  emit('submit', input.value)
  input.value = ''
}

function stopGeneration() {
  mdtApi.stopSession()
}

function renderMarkdown(text) {
  return md.render(text || '')
}

// Auto scroll to bottom
watch(chatHistory, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}, { deep: true })
</script>

<style>
.markdown-body p {
  margin-bottom: 0.5em;
}
.markdown-body ul {
  list-style-type: disc;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
}
</style>
