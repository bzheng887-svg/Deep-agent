<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{
  (e: 'session-selected', sessionId: string): void
  (e: 'session-created', sessionId: string): void
}>()

const sessions = ref<string[]>([])
const currentSession = ref<string>('')
const isLoading = ref(false)
const errorMsg = ref('')

import API_BASE from '../config'

const loadSessions = async () => {
  try {
    errorMsg.value = ''
    const res = await fetch(`${API_BASE}/api/sessions`)
    const data = await res.json()
    sessions.value = data.sessions || []
  } catch (e) {
    errorMsg.value = 'Failed to load sessions'
    console.error(e)
  }
}

const createNewSession = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' })
    const data = await res.json()
    const sessionId = data.session_id
    currentSession.value = sessionId
    sessions.value.unshift(sessionId)
    emit('session-created', sessionId)
    emit('session-selected', sessionId)
  } catch (e) {
    errorMsg.value = 'Failed to create session'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const selectExistingSession = async (sessionId: string) => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    await fetch(`${API_BASE}/api/sessions/${sessionId}`)
    currentSession.value = sessionId
    emit('session-selected', sessionId)
  } catch (e) {
    errorMsg.value = 'Failed to select session'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadSessions()
})
</script>

<template>
  <div class="session-sidebar">
    <div class="sidebar-header">
      <h3>Sessions</h3>
      <button @click="createNewSession" :disabled="isLoading" class="new-btn">
        {{ isLoading ? '...' : '+ New' }}
      </button>
    </div>
    <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
    <div class="session-list">
      <div v-if="sessions.length === 0" class="empty-state">
        No sessions
      </div>
      <div
        v-for="session in sessions"
        :key="session"
        :class="['session-item', { active: session === currentSession }]"
        @click="selectExistingSession(session)"
      >
        <span class="session-id">{{ session }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.session-sidebar {
  width: 240px;
  background: #16162a;
  border-right: 1px solid #2d2d44;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #2d2d44;
}
.sidebar-header h3 { margin: 0; font-size: 14px; color: #e0e0e0; }
.new-btn {
  padding: 6px 12px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}
.new-btn:disabled { background: #444; cursor: not-allowed; }
.error { padding: 8px 16px; color: #ff6b6b; font-size: 12px; }
.session-list { flex: 1; overflow-y: auto; padding: 8px; }
.empty-state { padding: 16px; text-align: center; color: #666; font-size: 13px; }
.session-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
}
.session-item:hover { background: #2d2d44; }
.session-item.active { background: #4a9eff; }
.session-id { font-size: 13px; color: #e0e0e0; font-family: monospace; }
.session-item.active .session-id { color: white; }
</style>