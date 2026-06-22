<script setup lang="ts">
import { ref } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import SessionSidebar from './components/SessionSidebar.vue'
import SkillManager from './components/SkillManager.vue'
import ToolManager from './components/ToolManager.vue'
import SettingsPage from './components/SettingsPage.vue'
import ToolSkillBrowser from './components/ToolSkillBrowser.vue'

const currentSession = ref('')
const activeTab = ref<'skills' | 'tools'>('skills')
const currentPage = ref<'chat' | 'settings' | 'browser'>('chat')

const handleSessionSelected = (sessionId: string) => {
  currentSession.value = sessionId
}

const handleSessionCreated = (sessionId: string) => {
  currentSession.value = sessionId
}
</script>

<template>
  <div class="app-container">
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="nav-brand">DeepClaw</div>
      <div class="nav-links">
        <button
          :class="['nav-btn', { active: currentPage === 'chat' }]"
          @click="currentPage = 'chat'"
        >
          Chat
        </button>
        <button
          :class="['nav-btn', { active: currentPage === 'settings' }]"
          @click="currentPage = 'settings'"
        >
          Settings
        </button>
        <button
          :class="['nav-btn', { active: currentPage === 'browser' }]"
          @click="currentPage = 'browser'"
        >
          Tools & Skills
        </button>
      </div>
    </nav>

    <!-- Main Content Area -->
    <div class="content-area">
      <!-- Settings Page -->
      <SettingsPage v-if="currentPage === 'settings'" />

      <!-- Tool/Skill Browser Page -->
      <ToolSkillBrowser v-else-if="currentPage === 'browser'" />

      <!-- Chat Page (default) -->
      <div v-else class="chat-layout">
        <!-- Left Sidebar: Sessions -->
        <SessionSidebar
          @session-selected="handleSessionSelected"
          @session-created="handleSessionCreated"
        />

        <!-- Main Chat Area -->
        <div class="main-area">
          <ChatWindow :session-id="currentSession" />
        </div>

        <!-- Right Sidebar: Skills/Tools -->
        <div class="right-sidebar">
          <div class="tab-header">
            <button
              :class="['tab-btn', { active: activeTab === 'skills' }]"
              @click="activeTab = 'skills'"
            >
              Skills
            </button>
            <button
              :class="['tab-btn', { active: activeTab === 'tools' }]"
              @click="activeTab = 'tools'"
            >
              Tools
            </button>
          </div>
          <div class="tab-content">
            <SkillManager v-if="activeTab === 'skills'" />
            <ToolManager v-else />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: #0f0f1a;
  color: #e0e0e0;
}
</style>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.top-nav {
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  background: #1a1a2e;
  border-bottom: 1px solid #2d2d44;
  flex-shrink: 0;
}

.nav-brand {
  font-size: 18px;
  font-weight: 600;
  color: #4a9eff;
  margin-right: 48px;
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #888;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #2d2d44;
  color: #e0e0e0;
}

.nav-btn.active {
  background: #4a9eff;
  color: white;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.right-sidebar {
  width: 300px;
  background: #1a1a2e;
  border-left: 1px solid #2d2d44;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #2d2d44;
}

.tab-btn {
  flex: 1;
  padding: 14px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #e0e0e0;
  background: #2d2d44;
}

.tab-btn.active {
  color: #4a9eff;
  border-bottom: 2px solid #4a9eff;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
</style>