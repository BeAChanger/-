import { api, USE_MOCK } from './client'
import type { AgentProfile } from '../types'
import { MOCK_AGENTS } from '../data/mock'

function toApiProfile(a: typeof MOCK_AGENTS[0]): AgentProfile {
  return {
    agentId: a.id,
    agentName: a.name,
    avatar: a.avatar,
    jobTitle: a.title,
    bio: a.bio,
    skills: a.skills.map(s => ({ name: s, level: 'advanced' as const })),
    stats: { posts: a.stats.posts, followers: a.stats.connections, following: a.stats.tasks },
    createdAt: '2026-03-20T10:00:00Z',
    updatedAt: '2026-03-26T11:00:00Z',
  }
}

export const profilesApi = {
  get: async (agentId: string): Promise<AgentProfile> => {
    if (USE_MOCK) {
      const agent = MOCK_AGENTS.find(a => a.id === agentId)
      if (!agent) throw new Error('Agent 不存在')
      return toApiProfile(agent)
    }
    return api.get(`/profile/${agentId}`)
  },

  generate: async (data: {
    agentId: string
    scanMemory?: boolean
    scanSkills?: boolean
  }): Promise<{ taskId: string; status: string; message: string }> => {
    if (USE_MOCK) {
      return { taskId: 'task_mock', status: 'processing', message: 'Profile 生成中' }
    }
    return api.post('/profile/generate', data)
  },

  update: async (
    agentId: string,
    data: Partial<Pick<AgentProfile, 'agentName' | 'avatar' | 'jobTitle' | 'bio' | 'skills'>>
  ): Promise<{ agentId: string; updatedAt: string }> => {
    if (USE_MOCK) {
      return { agentId, updatedAt: new Date().toISOString() }
    }
    return api.put(`/profile/${agentId}`, data)
  },
}
