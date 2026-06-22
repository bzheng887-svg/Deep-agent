<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listSkills, listTools } from '../api'

interface Skill {
  name: string
  path: string
  description: string
  type?: 'builtin' | 'external'
}

interface Tool {
  name: string
  path: string
  description: string
  type?: 'builtin' | 'external'
}

const skills = ref<Skill[]>([])
const tools = ref<Tool[]>([])
const isLoading = ref(false)
const activeCategory = ref<'all' | 'skills' | 'tools'>('all')
const filterType = ref<'all' | 'builtin' | 'external'>('all')

// Mock data for demonstration - internal/builtin items
const mockBuiltinSkills: Skill[] = [
  {
    name: 'skill-creator',
    path: 'backend/builtin-skills/skill-creator',
    description: 'Create, modify, and evaluate skills for the agent',
    type: 'builtin'
  },
  {
    name: 'tool-creator',
    path: 'backend/builtin-skills/tool-creator',
    description: 'Create and upgrade @tool functions',
    type: 'builtin'
  }
]

const mockBuiltinTools: Tool[] = [
  {
    name: 'code_executor',
    path: 'backend/deepagent/builtin_tools.py',
    description: 'Execute code in a sandboxed environment',
    type: 'builtin'
  },
  {
    name: 'file_operations',
    path: 'backend/deepagent/builtin_tools.py',
    description: 'Read, write, and manage files',
    type: 'builtin'
  }
]

const loadData = async () => {
  isLoading.value = true
  try {
    // Try loading from API
    const [skillsRes, toolsRes] = await Promise.allSettled([
      listSkills(),
      listTools()
    ])

    if (skillsRes.status === 'fulfilled') {
      skills.value = skillsRes.value.data.skills || []
    }
    if (toolsRes.status === 'fulfilled') {
      tools.value = toolsRes.value.data.tools || []
    }
  } catch (e) {
    console.error('Failed to load from API, using mock data:', e)
    // Use empty - will show only builtin items
  } finally {
    isLoading.value = false
  }
}

const filteredSkills = () => {
  let result = [...mockBuiltinSkills, ...skills.value]

  if (filterType.value === 'builtin') {
    result = result.filter(s => s.type === 'builtin')
  } else if (filterType.value === 'external') {
    result = result.filter(s => s.type === 'external')
  }

  return result
}

const filteredTools = () => {
  let result = [...mockBuiltinTools, ...tools.value]

  if (filterType.value === 'builtin') {
    result = result.filter(t => t.type === 'builtin')
  } else if (filterType.value === 'external') {
    result = result.filter(t => t.type === 'external')
  }

  return result
}

const allItems = () => {
  return [...filteredSkills(), ...filteredTools()]
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="browser-page">
    <div class="browser-header">
      <h2>Tools & Skills</h2>
      <p class="subtitle">Browse available internal and external tools and skills</p>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Category</label>
        <div class="filter-buttons">
          <button
            :class="{ active: activeCategory === 'all' }"
            @click="activeCategory = 'all'"
          >
            All
          </button>
          <button
            :class="{ active: activeCategory === 'skills' }"
            @click="activeCategory = 'skills'"
          >
            Skills
          </button>
          <button
            :class="{ active: activeCategory === 'tools' }"
            @click="activeCategory = 'tools'"
          >
            Tools
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label>Type</label>
        <div class="filter-buttons">
          <button
            :class="{ active: filterType === 'all' }"
            @click="filterType = 'all'"
          >
            All
          </button>
          <button
            :class="{ active: filterType === 'builtin' }"
            @click="filterType = 'builtin'"
          >
            Internal
          </button>
          <button
            :class="{ active: filterType === 'external' }"
            @click="filterType = 'external'"
          >
            External
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading">Loading...</div>

    <div v-else class="items-container">
      <!-- Skills Section -->
      <div
        v-if="activeCategory === 'all' || activeCategory === 'skills'"
        class="section"
      >
        <h3 class="section-title">
          <span class="section-icon">📚</span>
          Skills
          <span class="count">{{ filteredSkills().length }}</span>
        </h3>

        <div v-if="filteredSkills().length === 0" class="empty-state">
          No skills found
        </div>

        <div v-else class="item-list">
          <div
            v-for="skill in filteredSkills()"
            :key="skill.path"
            class="item-card"
          >
            <div class="item-header">
              <span class="item-name">{{ skill.name }}</span>
              <span
                :class="['item-type', skill.type || 'external']"
              >
                {{ skill.type === 'builtin' ? 'Internal' : 'External' }}
              </span>
            </div>
            <div class="item-path">{{ skill.path }}</div>
            <div v-if="skill.description" class="item-desc">
              {{ skill.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- Tools Section -->
      <div
        v-if="activeCategory === 'all' || activeCategory === 'tools'"
        class="section"
      >
        <h3 class="section-title">
          <span class="section-icon">🔧</span>
          Tools
          <span class="count">{{ filteredTools().length }}</span>
        </h3>

        <div v-if="filteredTools().length === 0" class="empty-state">
          No tools found
        </div>

        <div v-else class="item-list">
          <div
            v-for="tool in filteredTools()"
            :key="tool.path"
            class="item-card"
          >
            <div class="item-header">
              <span class="item-name">{{ tool.name }}</span>
              <span
                :class="['item-type', tool.type || 'external']"
              >
                {{ tool.type === 'builtin' ? 'Internal' : 'External' }}
              </span>
            </div>
            <div class="item-path">{{ tool.path }}</div>
            <div v-if="tool.description" class="item-desc">
              {{ tool.description }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.browser-page {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.browser-header {
  margin-bottom: 24px;
}

.browser-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.subtitle {
  color: #888;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px;
  background: #1a1a2e;
  border-radius: 12px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-buttons {
  display: flex;
  gap: 4px;
}

.filter-buttons button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: #2d2d44;
  color: #888;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-buttons button:hover {
  background: #3d3d54;
  color: #e0e0e0;
}

.filter-buttons button.active {
  background: #4a9eff;
  color: white;
}

.loading,
.empty-state {
  text-align: center;
  color: #666;
  font-size: 14px;
  padding: 40px;
}

.items-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2d2d44;
}

.section-icon {
  font-size: 18px;
}

.count {
  margin-left: auto;
  padding: 2px 8px;
  background: #2d2d44;
  border-radius: 12px;
  font-size: 12px;
  font-weight: normal;
  color: #888;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  padding: 16px;
  background: #16162a;
  border-radius: 8px;
  transition: all 0.2s;
}

.item-card:hover {
  background: #1d1d35;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #e0e0e0;
}

.item-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.item-type.builtin {
  background: rgba(74, 158, 255, 0.15);
  color: #4a9eff;
}

.item-type.external {
  background: rgba(255, 159, 67, 0.15);
  color: #ff9f43;
}

.item-path {
  font-size: 12px;
  color: #555;
  font-family: monospace;
  margin-bottom: 6px;
}

.item-desc {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
}
</style>