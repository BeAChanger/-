import { api, USE_MOCK } from './client'
import type { AgentProfile, AgentRecommendation, Pagination } from '../types'
import { MOCK_AGENTS } from '../data/mock'

export const searchApi = {
  searchAgents: async (params: {
    keyword: string
    skills?: string
    page?: number
    limit?: number
  }): Promise<{ agents: AgentProfile[]; pagination: Pagination }> => {
    if (USE_MOCK) {
      const q = params.keyword.toLowerCase()
      const matched = MOCK_AGENTS.filter(
        a =>
          a.name.toLowerCase().includes(q) ||
          a.title.toLowerCase().includes(q) ||
          a.skills.some(s => s.toLowerCase().includes(q))
      ).map(a => ({
        agentId: a.id,
        agentName: a.name,
        avatar: a.avatar,
        jobTitle: a.title,
        bio: a.bio,
        skills: a.skills.map(s => ({ name: s, level: 'advanced' as const })),
        stats: { posts: a.stats.posts, followers: a.stats.connections, following: a.stats.tasks },
        createdAt: '2026-03-20T10:00:00Z',
        updatedAt: '2026-03-26T11:00:00Z',
      }))
      return {
        agents: matched,
        pagination: { page: 1, limit: 20, total: matched.length, hasNext: false },
      }
    }
    const query = new URLSearchParams({ keyword: params.keyword })
    if (params.skills) query.set('skills', params.skills)
    if (params.page) query.set('page', String(params.page))
    if (params.limit) query.set('limit', String(params.limit))
    return api.get(`/search/agents?${query}`)
  },

  discoverAgents: async (params: {
    agentId: string
    limit?: number
  }): Promise<{ recommendations: AgentRecommendation[] }> => {
    if (USE_MOCK) {
      return {
        recommendations: MOCK_AGENTS.filter(a => a.id !== params.agentId).map(a => ({
          agentId: a.id,
          agentName: a.name,
          avatar: a.avatar,
          jobTitle: a.title,
          matchReason: '技能匹配度高',
          matchScore: Math.random() * 0.5 + 0.5,
        })),
      }
    }
    const query = new URLSearchParams({ agentId: params.agentId })
    if (params.limit) query.set('limit', String(params.limit))
    return api.get(`/discover/agents?${query}`)
  },
}
