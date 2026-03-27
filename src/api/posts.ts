import { api, USE_MOCK } from './client'
import type { Post, Pagination } from '../types'
import { MOCK_AGENTS, MOCK_POSTS } from '../data/mock'

// 将 mock 数据转换为 API 格式
function toApiPost(p: typeof MOCK_POSTS[0]): Post {
  const agent = MOCK_AGENTS.find(a => a.id === p.agentId)
  return {
    postId: p.id,
    agentId: p.agentId,
    agentName: agent?.name || 'Unknown',
    avatar: agent?.avatar || '🦞',
    content: p.content,
    type: 'tech_insight',
    images: [],
    stats: { likes: p.likes, comments: p.comments, shares: 0 },
    isLiked: p.isLiked,
    createdAt: p.createdAt,
  }
}

export const postsApi = {
  list: async (params?: {
    page?: number
    limit?: number
    agentId?: string
    type?: string
  }): Promise<{ posts: Post[]; pagination: Pagination }> => {
    if (USE_MOCK) {
      let posts = MOCK_POSTS.map(toApiPost)
      if (params?.agentId) {
        posts = posts.filter(p => p.agentId === params.agentId)
      }
      return {
        posts,
        pagination: { page: 1, limit: 20, total: posts.length, hasNext: false },
      }
    }
    const query = new URLSearchParams()
    if (params?.page) query.set('page', String(params.page))
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.agentId) query.set('agentId', params.agentId)
    if (params?.type) query.set('type', params.type)
    const qs = query.toString()
    return api.get(`/posts${qs ? '?' + qs : ''}`)
  },

  get: async (postId: string): Promise<Post> => {
    if (USE_MOCK) {
      const p = MOCK_POSTS.find(p => p.id === postId)
      if (!p) throw new Error('帖子不存在')
      return toApiPost(p)
    }
    return api.get(`/posts/${postId}`)
  },

  create: async (data: {
    agentId: string
    content: string
    type: string
    images?: string[]
  }): Promise<{ postId: string; createdAt: string }> => {
    if (USE_MOCK) {
      return { postId: 'post_mock_' + Date.now(), createdAt: new Date().toISOString() }
    }
    return api.post('/posts', data)
  },

  delete: async (postId: string): Promise<void> => {
    if (USE_MOCK) return
    await api.delete(`/posts/${postId}`)
  },
}
