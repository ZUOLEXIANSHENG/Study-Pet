const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export type StreamEvent = {
  type: string
  agent?: string
  content?: string
  value?: string
  result?: Record<string, unknown>
  confidence?: number
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return response.json() as Promise<T>
}

async function formRequest<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return response.json() as Promise<T>
}

async function streamRequest(
  path: string,
  payload: Record<string, unknown>,
  onEvent: (event: StreamEvent) => void,
) {
  const response = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  if (!response.body) {
    throw new Error('Streaming response body is not available')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.split('\n').find((item) => item.startsWith('data: '))
      if (!line) continue
      onEvent(JSON.parse(line.slice(6)) as StreamEvent)
    }
  }

  buffer += decoder.decode()
  if (buffer.trim()) {
    const line = buffer.split('\n').find((item) => item.startsWith('data: '))
    if (line) onEvent(JSON.parse(line.slice(6)) as StreamEvent)
  }
}

export const api = {
  generatePlan(payload: Record<string, unknown>) {
    return request('/plan/generate', { method: 'POST', body: JSON.stringify(payload) })
  },
  studyStart(payload: Record<string, unknown>) {
    return request('/study/start', { method: 'POST', body: JSON.stringify(payload) })
  },
  studyEnd(payload: Record<string, unknown>) {
    return request('/study/end', { method: 'POST', body: JSON.stringify(payload) })
  },
  growthUpdate(payload: Record<string, unknown>) {
    return request('/growth/update', { method: 'POST', body: JSON.stringify(payload) })
  },
  moodCheck(payload: Record<string, unknown>) {
    return request('/mood/check', { method: 'POST', body: JSON.stringify(payload) })
  },
  chat(payload: Record<string, unknown>) {
    return request('/chat', { method: 'POST', body: JSON.stringify(payload) })
  },
  chatStream(payload: Record<string, unknown>, onEvent: (event: StreamEvent) => void) {
    return streamRequest('/chat/stream', payload, onEvent)
  },
  generateImage(payload: Record<string, unknown>) {
    return request('/media/image/generate', { method: 'POST', body: JSON.stringify(payload) })
  },
  textToSpeech(payload: Record<string, unknown>) {
    return request('/audio/tts', { method: 'POST', body: JSON.stringify(payload) })
  },
  parseDocument(file: File, userId = 'demo') {
    const form = new FormData()
    form.append('file', file)
    return formRequest(`/document/parse?user_id=${encodeURIComponent(userId)}`, form)
  },
  generatePlanFromDocument(file: File, payload: Record<string, string | number>) {
    const form = new FormData()
    form.append('file', file)
    for (const [key, value] of Object.entries(payload)) {
      form.append(key, String(value))
    }
    return formRequest('/plan/generate-from-document', form)
  },
  events(userId = 'demo', limit = 20) {
    return request(`/events?user_id=${encodeURIComponent(userId)}&limit=${limit}`)
  },
  generateInteractive(payload: Record<string, unknown>) {
    return request('/interactive/generate', { method: 'POST', body: JSON.stringify(payload) })
  },
  completeInteractive(payload: Record<string, unknown>) {
    return request('/interactive/complete', { method: 'POST', body: JSON.stringify(payload) })
  },
  dailyReport(userId = 'demo') {
    return request(`/report/daily?user_id=${encodeURIComponent(userId)}`)
  },
  weeklyReport(userId = 'demo') {
    return request(`/report/weekly?user_id=${encodeURIComponent(userId)}`)
  },
}
