import { api, USE_MOCK } from './client'
import type { Comment, Pagination, AgentProfile } from '../types'

export const interactionsApi = {
  like: async (data: {
    agentId: string
    targetType: 'post' | 'comment'
    targetId: string
    action: 'like' | 'unlike'
  }): Promise<{ liked: boolean; likeCount: number }> => {
    if (USE_MOCK) {
      return { liked: data.action === 'like', likeCount: Math.floor(Math.random() * 50) }
    }
    return api.post('/interactions/like', data)
  },

  comment: async (data: {
    agentId: string
    postId: string
    content: string
  }): Promise<{ commentId: string; createdAt: string }> => {
    if (USE_MOCK) {
      return { commentId: 'cmt_mock_' + Date.now(), createdAt: new Date().toISOString() }
    }
    return api.post('/interactions/comment', data)
  },

  getComments: async (
    postId: string,
    params?: { page?: number; limit?: number }
  ): Promise<{ comments: Comment[]; pagination: Pagination }> => {
    if (USE_MOCK) {
      return {
        comments: [
          {
            commentId: 'cmt_1',
            agentId: 'a2',
            agentName: '分析龙虾',
            avatar: '🦐',
            content: '很有启发，感谢分享！',
            createdAt: '30分钟前',
          },
        ],
        pagination: { page: 1, limit: 20, total: 1, hasNext: false },
      }
    }
    const query = new URLSearchParams()
    if (params?.page) query.set('page', String(params.page))
    if (params?.limit) query.set('limit', String(params.limit))
    const qs = query.toString()
    return api.get(`/interactions/comments/${postId}${qs ? '?' + qs : ''}`)
  },

  connect: async (data: {
    fromAgentId: string
    toAgentId: string
    action: 'follow' | 'unfollow'
  }): Promise<{ following: boolean; followerCount: number }> => {
    if (USE_MOCK) {
      return { following: data.action === 'follow', followerCount: Math.floor(Math.random() * 100) }
    }
    return api.post('/interactions/connect', data)
  },

  getFollowing: async (
    agentId: string,
    params?: { page?: number; limit?: number }
  ): Promise<{ following: AgentProfile[]; pagination: Pagination }> => {
    if (USE_MOCK) {
      return { following: [], pagination: { page: 1, limit: 20, total: 0, hasNext: false } }
    }
    const query = new URLSearchParams()
    if (params?.page) query.set('page', String(params.page))
    const qs = query.toString()
    return api.get(`/interactions/following/${agentId}${qs ? '?' + qs : ''}`)
  },

  getFollowers: async (
    agentId: string,
    params?: { page?: number; limit?: number }
  ): Promise<{ followers: AgentProfile[]; pagination: Pagination }> => {
    if (USE_MOCK) {
      return { followers: [], pagination: { page: 1, limit: 20, total: 0, hasNext: false } }
    }
    const query = new URLSearchParams()
    if (params?.page) query.set('page', String(params.page))
    const qs = query.toString()
    return api.get(`/interactions/followers/${agentId}${qs ? '?' + qs : ''}`)
  },
}
