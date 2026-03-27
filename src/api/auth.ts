import { api, USE_MOCK, setAuth } from './client'
import type { AuthData, UserInfo } from '../types'

export const authApi = {
  register: async (data: {
    username: string
    email: string
    password: string
    agentName: string
  }): Promise<AuthData> => {
    if (USE_MOCK) {
      const mock: AuthData = {
        userId: 'user_001',
        agentId: 'agent_mock_1',
        token: 'mock_token_xxx',
      }
      setAuth(mock.token, mock.agentId)
      return mock
    }
    const result = await api.post<AuthData>('/auth/register', data)
    setAuth(result.token, result.agentId)
    return result
  },

  login: async (data: {
    email: string
    password: string
  }): Promise<AuthData> => {
    if (USE_MOCK) {
      const mock: AuthData = {
        userId: 'user_001',
        agentId: 'agent_mock_1',
        token: 'mock_token_xxx',
      }
      setAuth(mock.token, mock.agentId)
      return mock
    }
    const result = await api.post<AuthData>('/auth/login', data)
    setAuth(result.token, result.agentId)
    return result
  },

  me: async (): Promise<UserInfo> => {
    if (USE_MOCK) {
      return {
        userId: 'user_001',
        username: 'demo_user',
        email: 'demo@clawlink.com',
        agentId: 'agent_mock_1',
        createdAt: new Date().toISOString(),
      }
    }
    return api.get<UserInfo>('/auth/me')
  },
}
