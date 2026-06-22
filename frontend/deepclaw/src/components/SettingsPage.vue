<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface ModelConfig {
  apiUrl: string
  apiKey: string
  modelName: string
}

const settings = ref<ModelConfig>({
  apiUrl: 'https://api.deepseek.com/v1',
  apiKey: '',
  modelName: 'deepseek-chat'
})

const isSaving = ref(false)
const saveSuccess = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('deepclaw_settings')
  if (saved) {
    try {
      settings.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
  }
})

const handleSave = async () => {
  isSaving.value = true
  saveSuccess.value = false

  try {
    localStorage.setItem('deepclaw_settings', JSON.stringify(settings.value))
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to save settings:', e)
  } finally {
    isSaving.value = false
  }
}

const handleReset = () => {
  settings.value = {
    apiUrl: 'https://api.deepseek.com/v1',
    apiKey: '',
    modelName: 'deepseek-chat'
  }
  localStorage.removeItem('deepclaw_settings')
}
</script>

<template>
  <div class="settings-page">
    <div class="settings-header">
      <h2>Settings</h2>
      <p class="subtitle">Configure your model connection settings</p>
    </div>

    <div class="settings-form">
      <div class="form-group">
        <label for="apiUrl">API URL</label>
        <input
          id="apiUrl"
          v-model="settings.apiUrl"
          type="text"
          placeholder="https://api.deepseek.com/v1"
        />
        <span class="hint">Base URL for the model API provider</span>
      </div>

      <div class="form-group">
        <label for="modelName">Model Name</label>
        <input
          id="modelName"
          v-model="settings.modelName"
          type="text"
          placeholder="deepseek-chat"
        />
        <span class="hint">The model identifier (e.g., deepseek-chat, gpt-4o)</span>
      </div>

      <div class="form-group">
        <label for="apiKey">API Key</label>
        <input
          id="apiKey"
          v-model="settings.apiKey"
          type="password"
          placeholder="Enter your API key"
        />
        <span class="hint">Your API key for authentication</span>
      </div>

      <div class="form-actions">
        <button @click="handleReset" class="btn-secondary">
          Reset to Default
        </button>
        <button @click="handleSave" :disabled="isSaving" class="btn-primary">
          {{ isSaving ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>

      <div v-if="saveSuccess" class="success-message">
        Settings saved successfully!
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 32px;
}

.settings-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.subtitle {
  color: #888;
  font-size: 14px;
}

.settings-form {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #2d2d44;
  border-radius: 8px;
  background: #16162a;
  color: #e0e0e0;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4a9eff;
}

.form-group input::placeholder {
  color: #555;
}

.hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #666;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4a9eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3a8eef;
}

.btn-primary:disabled {
  background: #444;
  cursor: not-allowed;
}

.btn-secondary {
  background: #2d2d44;
  color: #e0e0e0;
}

.btn-secondary:hover {
  background: #3d3d54;
}

.success-message {
  margin-top: 16px;
  padding: 12px;
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid #4a9eff;
  border-radius: 8px;
  color: #4a9eff;
  font-size: 14px;
  text-align: center;
}
</style>