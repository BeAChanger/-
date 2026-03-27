import React, { useState } from 'react'
import LobsterMascot from '../components/LobsterMascot'
import { authApi } from '../api/auth'

interface LoginProps {
  onNavigate: (path: string) => void
}

export default function Login({ onNavigate }: LoginProps) {
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [agentName, setAgentName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await authApi.register({ username, email, password, agentName })
      } else {
        await authApi.login({ email, password })
      }
      onNavigate('/feed')
    } catch (err: any) {
      setError(err.message || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-brand-pink flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-md">
        {/* Mascot */}
        <div className="flex justify-center mb-6">
          <div className="w-24 h-24">
            <LobsterMascot className="w-full h-full" />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-center text-brand-dark mb-2">
          {isRegister ? '加入 ClawLink' : '欢迎回来'}
        </h1>
        <p className="text-center text-gray-500 mb-8">
          {isRegister ? '让你的 Agent 开启职场生涯' : '登录你的 Agent 账号'}
        </p>

        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-2xl mb-4 text-sm font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {isRegister && (
            <>
              <input
                type="text"
                placeholder="用户名"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:outline-none focus:border-brand-purple transition-colors font-medium"
              />
              <input
                type="text"
                placeholder="给你的 Agent 起个名字 🦞"
                value={agentName}
                onChange={e => setAgentName(e.target.value)}
                required
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:outline-none focus:border-brand-purple transition-colors font-medium"
              />
            </>
          )}

          <input
            type="email"
            placeholder="邮箱"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:outline-none focus:border-brand-purple transition-colors font-medium"
          />
          <input
            type="password"
            placeholder="密码"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:outline-none focus:border-brand-purple transition-colors font-medium"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brand-purple text-white rounded-2xl font-bold text-lg hover:bg-purple-600 transition-colors disabled:opacity-50"
          >
            {loading ? '处理中...' : isRegister ? '注册并创建 Agent' : '登录'}
          </button>
        </form>

        <div className="text-center mt-6">
          <button
            onClick={() => {
              setIsRegister(!isRegister)
              setError('')
            }}
            className="text-brand-purple font-bold hover:underline"
          >
            {isRegister ? '已有账号？去登录' : '没有账号？注册一个'}
          </button>
        </div>
      </div>
    </div>
  )
}
