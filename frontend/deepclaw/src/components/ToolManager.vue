<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listTools, addTool } from '../api'

interface Tool {
  name: string
  path: string
  description: string
}

const tools = ref<Tool[]>([])
const isLoading = ref(false)
const showAddForm = ref(false)
const newToolPath = ref('')
const newToolName = ref('')
const newToolDesc = ref('')

const loadTools = async () => {
  isLoading.value = true
  try {
    const res = await listTools()
    tools.value = res.data.tools || []
  } catch (e) {
    console.error('Failed to load tools:', e)
  } finally {
    isLoading.value = false
  }
}

const handleAddTool = async () => {
  if (!newToolPath.value.trim()) return

  isLoading.value = true
  try {
    await addTool(newToolName.value || newToolPath.value.split('/').pop() || 'tool', newToolPath.value, newToolDesc.value)
    newToolPath.value = ''
    newToolName.value = ''
    newToolDesc.value = ''
    showAddForm.value = false
    await loadTools()
  } catch (e) {
    console.error('Failed to add tool:', e)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadTools()
})
</script>

<template>
  <div class="tool-manager">
    <div class="panel-header">
      <h3>Tools</h3>
      <button @click="showAddForm = !showAddForm" class="toggle-btn">
        {{ showAddForm ? 'Cancel' : '+ Add' }}
      </button>
    </div>

    <div v-if="showAddForm" class="add-form">
      <input v-model="newToolPath" placeholder="Tool file path (.py)" />
      <input v-model="newToolName" placeholder="Tool name (optional)" />
      <input v-model="newToolDesc" placeholder="Description (optional)" />
      <button @click="handleAddTool" :disabled="isLoading || !newToolPath.trim()">
        Add Tool
      </button>
    </div>

    <div v-if="isLoading && !showAddForm" class="loading">Loading...</div>

    <div v-else-if="tools.length === 0" class="empty-state">
      No tools available
    </div>

    <div v-else class="tool-list">
      <div v-for="tool in tools" :key="tool.path" class="tool-item">
        <div class="tool-name">{{ tool.name }}</div>
        <div v-if="tool.description" class="tool-desc">{{ tool.description }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tool-manager {
  background: #16162a;
  border-radius: 8px;
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  color: #e0e0e0;
}

.toggle-btn {
  padding: 6px 12px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
  padding: 12px;
  background: #1a1a2e;
  border-radius: 6px;
}

.add-form input {
  padding: 8px;
  border: 1px solid #2d2d44;
  border-radius: 4px;
  background: #16162a;
  color: #e0e0e0;
  font-size: 13px;
}

.add-form input:focus {
  outline: none;
  border-color: #4a9eff;
}

.add-form button {
  padding: 8px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-form button:disabled {
  background: #444;
  cursor: not-allowed;
}

.loading, .empty-state {
  text-align: center;
  color: #666;
  font-size: 13px;
  padding: 12px;
}

.tool-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-item {
  padding: 10px 12px;
  background: #1a1a2e;
  border-radius: 6px;
}

.tool-name {
  font-size: 13px;
  color: #e0e0e0;
  font-weight: 500;
}

.tool-desc {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>