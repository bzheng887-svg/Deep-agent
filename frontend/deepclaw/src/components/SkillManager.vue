<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listSkills, addSkill } from '../api'

interface Skill {
  name: string
  path: string
  description: string
}

const skills = ref<Skill[]>([])
const isLoading = ref(false)
const showAddForm = ref(false)
const newSkillPath = ref('')
const newSkillName = ref('')
const newSkillDesc = ref('')

const loadSkills = async () => {
  isLoading.value = true
  try {
    const res = await listSkills()
    skills.value = res.data.skills || []
  } catch (e) {
    console.error('Failed to load skills:', e)
  } finally {
    isLoading.value = false
  }
}

const handleAddSkill = async () => {
  if (!newSkillPath.value.trim()) return

  isLoading.value = true
  try {
    await addSkill(newSkillName.value || newSkillPath.value.split('/').pop() || 'skill', newSkillPath.value, newSkillDesc.value)
    newSkillPath.value = ''
    newSkillName.value = ''
    newSkillDesc.value = ''
    showAddForm.value = false
    await loadSkills()
  } catch (e) {
    console.error('Failed to add skill:', e)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadSkills()
})
</script>

<template>
  <div class="skill-manager">
    <div class="panel-header">
      <h3>Skills</h3>
      <button @click="showAddForm = !showAddForm" class="toggle-btn">
        {{ showAddForm ? 'Cancel' : '+ Add' }}
      </button>
    </div>

    <div v-if="showAddForm" class="add-form">
      <input v-model="newSkillPath" placeholder="Skill folder path" />
      <input v-model="newSkillName" placeholder="Skill name (optional)" />
      <input v-model="newSkillDesc" placeholder="Description (optional)" />
      <button @click="handleAddSkill" :disabled="isLoading || !newSkillPath.trim()">
        Add Skill
      </button>
    </div>

    <div v-if="isLoading && !showAddForm" class="loading">Loading...</div>

    <div v-else-if="skills.length === 0" class="empty-state">
      No skills available
    </div>

    <div v-else class="skill-list">
      <div v-for="skill in skills" :key="skill.path" class="skill-item">
        <div class="skill-name">{{ skill.name }}</div>
        <div v-if="skill.description" class="skill-desc">{{ skill.description }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skill-manager {
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

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-item {
  padding: 10px 12px;
  background: #1a1a2e;
  border-radius: 6px;
}

.skill-name {
  font-size: 13px;
  color: #e0e0e0;
  font-weight: 500;
}

.skill-desc {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>