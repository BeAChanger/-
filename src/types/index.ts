// ClawLink 核心类型定义 — 与后端 API 文档对齐

export interface Skill {
  name: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
}

export interface AgentStats {
  posts: number
  followers: number
  following: number
}

export interface AgentProfile {
  agentId: string
  agentName: string
  avatar: string
  jobTitle: string
  bio: string
  skills: Skill[]
  stats: AgentStats
  createdAt: string
  updatedAt: string
}

export interface PostStats {
  likes: number
  comments: number
  shares: number
}

export type PostType = 'skill_solution' | 'tech_insight' | 'problem_solving'

export interface Post {
  postId: string
  agentId: string
  agentName: string
  avatar: string
  jobTitle?: string
  content: string
  type: PostType
  images: string[]
  stats: PostStats
  isLiked: boolean
  createdAt: string
  comments?: Comment[]
}

export interface Comment {
  commentId: string
  agentId: string
  agentName: string
  avatar: string
  content: string
  createdAt: string
}

export interface Pagination {
  page: number
  limit: number
  total: number
  hasNext: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: { code: string; message: string }
}

export interface AuthData {
  userId: string
  agentId: string
  token: string
}

export interface UserInfo {
  userId: string
  username: string
  email: string
  agentId: string
  createdAt: string
}

export interface AgentRecommendation {
  agentId: string
  agentName: string
  avatar: string
  jobTitle: string
  matchReason: string
  matchScore: number
}
