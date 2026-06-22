import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

// Create axios instance with timeout
const axiosInstance = axios.create({
  timeout: 10000, // 10 seconds timeout
})

// Session APIs
export const createSession = () => axiosInstance.post(`${API_BASE}/api/sessions`)
export const listSessions = () => axiosInstance.get(`${API_BASE}/api/sessions`)
export const selectSession = (sessionId: string) => axiosInstance.get(`${API_BASE}/api/sessions/${sessionId}`)

// Chat API (SSE) - POST with text in body
export const sendMessage = (text: string, sessionId?: string) => {
  return new EventSource(`${API_BASE}/api/chat?text=${encodeURIComponent(text)}&session_id=${sessionId || ''}`)
}

// Skills APIs
export const listSkills = () => axiosInstance.get(`${API_BASE}/api/skills`)
export const addSkill = (name: string, path: string, description: string) =>
  axiosInstance.post(`${API_BASE}/api/skills`, { name, path, description })

// Tools APIs
export const listTools = () => axiosInstance.get(`${API_BASE}/api/tools`)
export const addTool = (name: string, path: string, description: string) =>
  axiosInstance.post(`${API_BASE}/api/tools`, { name, path, description })

export default {
  createSession,
  listSessions,
  selectSession,
  sendMessage,
  listSkills,
  addSkill,
  listTools,
  addTool,
}