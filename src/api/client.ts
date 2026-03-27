// API Client — 统一封装，响应拦截器自动解包 data
import type { ApiResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export { USE_MOCK }

function getToken(): string | null {
  try {
    const raw = localStorage.getItem('clawlink-auth')
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return parsed.token || null
  } catch {
    return null
  }
}

export function setAuth(token: string, agentId: string) {
  localStorage.setItem('clawlink-auth', JSON.stringify({ token, agentId }))
}

export function getAuth(): { token: string; agentId: string } | null {
  try {
    const raw = localStorage.getItem('clawlink-auth')
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (parsed.token && parsed.agentId) return parsed
    return null
  } catch {
    return null
  }
}

export function clearAuth() {
  localStorage.removeItem('clawlink-auth')
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    clearAuth()
    window.location.href = '/login'
    throw new Error('认证已过期，请重新登录')
  }

  const json: ApiResponse<T> = await res.json()

  if (!json.success) {
    throw new Error(json.error?.message || json.message || '请求失败')
  }

  return json.data
}

export const api = {
  get: <T>(path: string) => request<T>(path),

  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string) =>
    request<T>(path, { method: 'DELETE' }),
}
