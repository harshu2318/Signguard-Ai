/**
 * SignGuard AI — Axios API Layer
 * All backend communication in one place.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

/**
 * Upload a signature image and get a prediction.
 * @param {File} file - Image file to upload
 * @returns {{ prediction: string, confidence: number, filename: string }}
 */
export const uploadSignature = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

/**
 * Send a question to the RAG chatbot.
 * @param {{ question: string, prediction?: string, confidence?: number }} payload
 * @returns {{ answer: string }}
 */
export const sendMessage = async ({ question, prediction, confidence }) => {
  const response = await api.post('/chat', {
    question,
    prediction: prediction ?? null,
    confidence: confidence ?? null,
  })
  return response.data
}
