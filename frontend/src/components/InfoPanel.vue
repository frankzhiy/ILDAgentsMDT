<template>
  <div class="h-full flex flex-col bg-white">
    <el-tabs v-model="activeTab" class="flex-1 flex flex-col h-full" type="border-card">
      
      <!-- Tab 1: Structured Info -->
      <el-tab-pane label="结构化信息" name="structured" class="h-full overflow-y-auto">
        <div v-if="Object.keys(structuredInfo).length === 0 && !streamingStructuredText" class="text-gray-400 text-center mt-10">
          暂无结构化数据
        </div>
        <div v-else-if="streamingStructuredText && Object.keys(structuredInfo).length === 0" class="text-xs bg-gray-50 p-4 rounded border border-gray-200 overflow-auto whitespace-pre-wrap font-mono">
          {{ streamingStructuredText }}
        </div>
        <div v-else class="p-4">
          <vue-json-pretty 
            :data="structuredInfo" 
            :deep="2" 
            :show-length="true" 
            :show-line="false"
            :show-double-quotes="false"
            :highlight-mouseover-node="true"
          />
        </div>
      </el-tab-pane>

      <!-- Tab 2: Specialist Opinions -->
      <el-tab-pane label="专科意见" name="opinions" class="h-full overflow-y-auto">
        <div v-if="roundHistory.length === 0 && Object.keys(specialistOpinions).length === 0" class="text-gray-400 text-center mt-10">
          暂无专科意见
        </div>
        
        <div class="space-y-6 p-4">
          <!-- History Rounds -->
          <div v-for="round in roundHistory" :key="round.round" class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600 border-b border-gray-200">
              第 {{ round.round + 1 }} 轮讨论
            </div>
            <el-collapse>
              <el-collapse-item v-for="(opinion, role) in filterSpecialists(round.opinions)" :key="role" :title="role" :name="role + round.round">
                <div class="text-sm text-gray-700 markdown-body" v-html="renderMarkdown(opinion)"></div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- Current Round -->
          <div v-if="Object.keys(filterSpecialists(specialistOpinions)).length > 0" class="border border-blue-100 rounded-lg overflow-hidden shadow-sm">
            <div class="bg-blue-50 px-4 py-2 text-xs font-bold text-blue-600 border-b border-blue-100 flex items-center gap-2">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              当前讨论 (第 {{ currentRoundNumber + 1 }} 轮)
            </div>
            <el-collapse v-model="activeCollapseItems">
              <el-collapse-item v-for="(opinion, role) in filterSpecialists(specialistOpinions)" :key="role" :title="role" :name="role">
                <div class="text-sm text-gray-700 markdown-body" v-html="renderMarkdown(opinion)"></div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 3: Specialist Summaries -->
      <el-tab-pane label="专科总结意见" name="specialist_summaries" class="h-full overflow-y-auto">
        <div v-if="roundHistory.length === 0 && Object.keys(filterSpecialists(specialistSummaries)).length === 0" class="text-gray-400 text-center mt-10">
          暂无专科总结
        </div>
        
        <div class="space-y-6 p-4">
          <!-- History Rounds -->
          <div v-for="round in roundHistory" :key="round.round" class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600 border-b border-gray-200">
              第 {{ round.round + 1 }} 轮总结
            </div>
            <el-collapse>
              <el-collapse-item v-for="(summary, role) in filterSpecialists(round.summaries)" :key="role" :title="role" :name="role + round.round + '_summary'">
                <div class="text-sm text-gray-700 markdown-body" v-html="renderMarkdown(summary)"></div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- Current Round -->
          <div v-if="Object.keys(filterSpecialists(specialistSummaries)).length > 0" class="border border-purple-100 rounded-lg overflow-hidden shadow-sm">
            <div class="bg-purple-50 px-4 py-2 text-xs font-bold text-purple-600 border-b border-purple-100 flex items-center gap-2">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
              </span>
              当前总结 (第 {{ currentRoundNumber + 1 }} 轮)
            </div>
            <el-collapse v-model="activeSummaryCollapseItems">
              <el-collapse-item v-for="(summary, role) in filterSpecialists(specialistSummaries)" :key="role" :title="role" :name="role + '_summary'">
                <div class="text-sm text-gray-700 markdown-body" v-html="renderMarkdown(summary)"></div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 4: Conflicts -->
      <el-tab-pane label="冲突检测" name="conflicts" class="h-full overflow-y-auto">
        <div v-if="roundHistory.length === 0 && conflicts.length === 0" class="text-gray-400 text-center mt-10">
          未检测到明显冲突
        </div>
        
        <div class="space-y-6 p-4">
          <!-- History Rounds -->
          <div v-for="round in roundHistory" :key="round.round">
            <div v-if="round.conflicts && round.conflicts.length > 0" class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600 border-b border-gray-200">
                第 {{ round.round + 1 }} 轮冲突检测
              </div>
              <div class="p-4 space-y-4">
                <div v-for="(conflict, index) in round.conflicts" :key="index" class="border border-red-200 rounded-lg p-4 bg-red-50">
                  <div class="flex items-center gap-2 mb-2">
                    <el-tag type="danger" effect="dark" size="small">{{ conflict.severity || 'High' }}</el-tag>
                    <span class="font-bold text-red-800">冲突点 {{ index + 1 }}</span>
                  </div>
                  <div class="text-sm text-gray-800 font-medium mb-2">{{ conflict.issue }}</div>
                  <div class="text-xs text-gray-600 bg-white p-2 rounded border border-red-100">
                    {{ conflict.description }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Round -->
          <div v-if="conflicts.length > 0" class="border rounded-lg overflow-hidden shadow-sm" :class="conflicts[0].severity === 'success' ? 'border-green-100' : (conflicts[0].severity === 'info' ? 'border-blue-100' : 'border-red-100')">
            <div class="px-4 py-2 text-xs font-bold border-b flex items-center gap-2" :class="conflicts[0].severity === 'success' ? 'bg-green-50 text-green-600 border-green-100' : (conflicts[0].severity === 'info' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-red-50 text-red-600 border-red-100')">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="conflicts[0].severity === 'success' ? 'bg-green-400' : (conflicts[0].severity === 'info' ? 'bg-blue-400' : 'bg-red-400')"></span>
                <span class="relative inline-flex rounded-full h-2 w-2" :class="conflicts[0].severity === 'success' ? 'bg-green-500' : (conflicts[0].severity === 'info' ? 'bg-blue-500' : 'bg-red-500')"></span>
              </span>
              当前冲突检测 (第 {{ currentRoundNumber + 1 }} 轮)
            </div>
            <div class="p-4 space-y-4">
              <div v-for="(conflict, index) in conflicts" :key="index" class="border rounded-lg p-4" :class="conflict.severity === 'success' ? 'border-green-200 bg-green-50' : (conflict.severity === 'info' ? 'border-blue-200 bg-blue-50' : 'border-red-200 bg-red-50')">
                <div class="flex items-center gap-2 mb-2">
                  <el-tag :type="conflict.severity === 'success' ? 'success' : (conflict.severity === 'info' ? 'info' : 'danger')" effect="dark" size="small">{{ conflict.severity || 'High' }}</el-tag>
                  <span class="font-bold" :class="conflict.severity === 'success' ? 'text-green-800' : (conflict.severity === 'info' ? 'text-blue-800' : 'text-red-800')">
                    {{ conflict.severity === 'success' || conflict.severity === 'info' ? '检测结果' : '冲突点 ' + (index + 1) }}
                  </span>
                </div>
                <div class="text-sm font-medium mb-2" :class="conflict.severity === 'success' ? 'text-green-800' : (conflict.severity === 'info' ? 'text-blue-800' : 'text-gray-800')">{{ conflict.issue }}</div>
                <div class="text-xs bg-white p-2 rounded border" :class="conflict.severity === 'success' ? 'text-green-600 border-green-100' : (conflict.severity === 'info' ? 'text-blue-600 border-blue-100' : 'text-gray-600 border-red-100')">
                  {{ conflict.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 5: Team Discussion -->
      <el-tab-pane label="团队讨论" name="discussion" class="h-full overflow-y-auto">
        <div v-if="roundHistory.length === 0 && !discussionNotes" class="text-gray-400 text-center mt-10">
          暂无讨论纪要
        </div>
        
        <div class="space-y-6 p-4">
          <!-- History Rounds -->
          <div v-for="round in roundHistory" :key="round.round">
            <div v-if="round.discussionNotes" class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600 border-b border-gray-200">
                第 {{ round.round + 1 }} 轮讨论纪要
              </div>
              <div class="p-4 bg-yellow-50">
                <div class="text-sm text-gray-800 markdown-body" v-html="renderMarkdown(round.discussionNotes)"></div>
              </div>
            </div>
          </div>

          <!-- Current Round -->
          <div v-if="discussionNotes" class="border border-yellow-100 rounded-lg overflow-hidden shadow-sm">
            <div class="bg-yellow-50 px-4 py-2 text-xs font-bold text-yellow-600 border-b border-yellow-100 flex items-center gap-2">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
              </span>
              当前讨论纪要 (第 {{ currentRoundNumber + 1 }} 轮)
            </div>
            <div class="p-4 bg-yellow-50">
              <div class="text-sm text-gray-800 markdown-body" v-html="renderMarkdown(discussionNotes)"></div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 6: Moderator Summary -->
      <el-tab-pane label="最终结论" name="summary" class="h-full overflow-y-auto">
        <div v-if="roundHistory.length === 0 && !moderatorSummary" class="text-gray-400 text-center mt-10">
          等待主持专家总结...
        </div>
        
        <div class="space-y-6 p-4">
          <!-- History Summaries -->
          <div v-for="round in roundHistory" :key="round.round">
            <div v-if="round.summary" class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600 border-b border-gray-200">
                第 {{ round.round + 1 }} 轮总结
              </div>
              <div class="p-4 text-sm text-gray-800 leading-relaxed markdown-body" v-html="renderMarkdown(round.summary)"></div>
            </div>
          </div>

          <!-- Current Summary -->
          <div v-if="moderatorSummary" class="border border-green-100 rounded-lg overflow-hidden shadow-sm">
            <div class="bg-green-50 px-4 py-2 text-xs font-bold text-green-600 border-b border-green-100">
              当前总结 (第 {{ currentRoundNumber + 1 }} 轮)
            </div>
            <div class="p-4 text-sm text-gray-800 leading-relaxed markdown-body" v-html="renderMarkdown(moderatorSummary)"></div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 7: Logs -->
      <el-tab-pane label="系统日志" name="logs" class="h-full overflow-y-auto">
        <div class="font-mono text-xs space-y-1">
          <div v-for="(log, index) in executionLogs" :key="index" class="border-b border-gray-100 py-1">
            {{ log }}
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useClinicalStore } from '../stores/clinicalStore'
import { useConnectionStore } from '../stores/connectionStore'
import { storeToRefs } from 'pinia'
import VueJsonPretty from 'vue-json-pretty'
import 'vue-json-pretty/lib/styles.css'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const store = useClinicalStore()
const connectionStore = useConnectionStore()
const { executionLogs } = storeToRefs(connectionStore)
const { 
  structuredInfo, 
  specialistOpinions, 
  specialistSummaries, 
  moderatorSummary, 
  roundHistory, 
  currentRoundNumber,
  streamingStructuredText,
  conflicts,
  discussionNotes
} = storeToRefs(store)

const activeTab = ref('structured')
const activeCollapseItems = ref([])
const activeSummaryCollapseItems = ref([])

function renderMarkdown(text) {
  return md.render(text || '')
}

function filterSpecialists(data) {
  if (!data) return {}
  const filtered = { ...data }
  delete filtered['Case Organizer']
  return filtered
}

// Auto expand collapse item when new opinion starts streaming
watch(specialistOpinions, (newVal) => {
  Object.keys(newVal).forEach(role => {
    if (role !== 'Case Organizer' && newVal[role] && !activeCollapseItems.value.includes(role)) {
      activeCollapseItems.value.push(role)
    }
  })
}, { deep: true })

// Auto expand summary collapse item
watch(specialistSummaries, (newVal) => {
  Object.keys(newVal).forEach(role => {
    if (role !== 'Case Organizer' && newVal[role] && !activeSummaryCollapseItems.value.includes(role + '_summary')) {
      activeSummaryCollapseItems.value.push(role + '_summary')
    }
  })
}, { deep: true })
</script>

<style scoped>
:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  padding: 0 !important;
}
:deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
}
/* Markdown Styles for Opinions */
:deep(.markdown-body p) {
  margin-bottom: 0.5em;
}
:deep(.markdown-body ul) {
  list-style-type: disc;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
}
:deep(.markdown-body h1), :deep(.markdown-body h2), :deep(.markdown-body h3) {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
}
</style>
