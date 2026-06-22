<script setup lang="ts">
import { ref, watch, onUnmounted, nextTick } from 'vue'

const props = defineProps<{
  sessionId: string
}>()

import API_BASE from '../config'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputText = ref('')
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

watch(() => props.sessionId, () => {
  messages.value = []
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const send = async () => {
  if (!inputText.value.trim() || isStreaming.value) return
  if (!props.sessionId) {
    alert('Please select or create a session first')
    return
  }

  const text = inputText.value
  inputText.value = ''
  isStreaming.value = true

  messages.value.push({ id: Date.now().toString(), role: 'user', content: text })
  messages.value.push({ id: (Date.now() + 1).toString(), role: 'assistant', content: '' })
  scrollToBottom()

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, session_id: props.sessionId }),
    })

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            const lastMsg = messages.value[messages.value.length - 1]

            if (data.event === 'assistant_message') {
              lastMsg.content += data.data.content
              scrollToBottom()
            } else if (data.event === 'Middleware_before_tool') {
              lastMsg.content += `\n\n[Tool: ${data.data.tool_name}]`
              scrollToBottom()
            } else if (data.event === 'done') {
              isStreaming.value = false
            } else if (data.event === 'error') {
              lastMsg.content = `Error: ${data.data.message}`
              isStreaming.value = false
            }
          } catch {}
        }
      }
    }
  } catch (e) {
    console.error('Chat error:', e)
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg) lastMsg.content = 'Connection error'
  }
  isStreaming.value = false
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<template>
  <div class="chat-window">
    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <p>{{ sessionId ? 'No messages yet. Start a conversation!' : 'Select or create a session' }}</p>
      </div>
      <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
        <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-content"><pre>{{ msg.content }}</pre></div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="inputText"
        :disabled="isStreaming || !sessionId"
        @keydown="handleKeydown"
        placeholder="Type your message..."
      ></textarea>
      <button @click="send" :disabled="isStreaming || !inputText.trim() || !sessionId">
        {{ isStreaming ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-window { display: flex; flex-direction: column; height: 100%; background: #1a1a2e; }
.messages-container { flex: 1; overflow-y: auto; padding: 16px; }
.empty-state { display: flex; align-items: center; justify-content: center; height: 100%; color: #666; }
.message { display: flex; gap: 12px; margin-bottom: 16px; }
.message.user { flex-direction: row-reverse; }
.message-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.message.user .message-avatar { background: #4a9eff; }
.message.assistant .message-avatar { background: #2d2d44; }
.message-content { max-width: 70%; padding: 12px 16px; border-radius: 12px; }
.message.user .message-content { background: #4a9eff; color: white; }
.message.assistant .message-content { background: #2d2d44; color: #e0e0e0; }
.message-content pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; font-family: inherit; }
.input-area { display: flex; gap: 8px; padding: 16px; background: #16162a; border-top: 1px solid #2d2d44; }
.input-area textarea { flex: 1; padding: 12px; border: 1px solid #2d2d44; border-radius: 8px; background: #1a1a2e; color: #e0e0e0; resize: none; font-family: inherit; font-size: 14px; min-height: 44px; max-height: 120px; }
.input-area textarea:focus { outline: none; border-color: #4a9eff; }
.input-area button { padding: 12px 24px; background: #4a9eff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; }
.input-area button:disabled { background: #444; cursor: not-allowed; }
</style>