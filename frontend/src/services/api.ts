const BASE = 'http://localhost:8000/api'

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
  dailyReport(userId = 'demo') {
    return request(`/report/daily?user_id=${encodeURIComponent(userId)}`)
  },
  weeklyReport(userId = 'demo') {
    return request(`/report/weekly?user_id=${encodeURIComponent(userId)}`)
  },
}
