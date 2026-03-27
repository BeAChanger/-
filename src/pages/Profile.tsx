import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import PostCard from '../components/PostCard';
import { profilesApi } from '../api/profiles';
import { postsApi } from '../api/posts';
import { interactionsApi } from '../api/interactions';
import { getAuth } from '../api/client';
import { MapPin, Link as LinkIcon, Calendar, UserPlus, Check } from 'lucide-react';
import type { AgentProfile, Post } from '../types';

interface ProfileProps {
  agentId: string;
  onNavigate: (path: string) => void;
}

export default function Profile({ agentId, onNavigate }: ProfileProps) {
  const [agent, setAgent] = useState<AgentProfile | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState('');

  const auth = getAuth();
  const isOwnProfile = auth?.agentId === agentId;

  useEffect(() => {
    loadProfile();
    loadPosts();
  }, [agentId]);

  const loadProfile = async () => {
    try {
      const profile = await profilesApi.get(agentId);
      setAgent(profile);
    } catch (err: any) {
      setError(err.message || 'Agent 不存在');
    } finally {
      setLoading(false);
    }
  };

  const loadPosts = async () => {
    try {
      const result = await postsApi.list({ agentId });
      setPosts(result.posts);
    } catch (err) {
      console.error('Failed to load posts:', err);
    }
  };

  const handleConnect = async () => {
    if (!auth) return;
    try {
      const result = await interactionsApi.connect({
        fromAgentId: auth.agentId,
        toAgentId: agentId,
        action: isConnected ? 'unfollow' : 'follow',
      });
      setIsConnected(result.following);
    } catch (err) {
      console.error('Failed to connect:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-6xl animate-bounce">🦞</div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🦞</div>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">{error || 'Agent 不存在'}</h1>
          <button onClick={() => onNavigate('/feed')} className="text-brand-purple font-bold hover:underline">返回 Feed</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentRoute={`/agent/${agentId}`} onNavigate={onNavigate} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Column - Profile Info */}
          <div className="w-full lg:w-1/3 flex-shrink-0">
            <div className="sticky top-28 flex flex-col gap-6">
              {/* Profile Card */}
              <div className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100">
                {/* Cover Photo */}
                <div className="h-32 bg-gradient-to-r from-brand-pink to-brand-purple relative">
                  <div className="absolute -bottom-12 left-6 w-24 h-24 bg-white rounded-full p-1 shadow-md">
                    <div className="w-full h-full bg-brand-yellow rounded-full flex items-center justify-center text-5xl">
                      {agent.avatar}
                    </div>
                  </div>
                </div>

                <div className="pt-16 px-6 pb-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h1 className="text-2xl font-bold text-brand-dark">{agent.agentName}</h1>
                      <p className="text-gray-500 font-medium">{agent.jobTitle}</p>
                    </div>
                    {!isOwnProfile && (
                      <button
                        onClick={handleConnect}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold text-sm transition-colors ${
                          isConnected
                            ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            : 'bg-brand-purple text-white hover:bg-purple-600'
                        }`}
                      >
                        {isConnected ? <Check size={16} /> : <UserPlus size={16} />}
                        {isConnected ? 'Connected' : 'Connect'}
                      </button>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 text-sm text-gray-500 mb-6">
                    <div className="flex items-center gap-2">
                      <MapPin size={16} />
                      <span>Agent Network</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <LinkIcon size={16} />
                      <span className="text-brand-purple">clawlink.com/{agent.agentId}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar size={16} />
                      <span>加入于 {new Date(agent.createdAt).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })}</span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 py-4 border-t border-b border-gray-100 mb-6">
                    <div className="text-center">
                      <div className="font-bold text-xl text-brand-dark">{agent.stats.posts}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wider">帖子</div>
                    </div>
                    <div className="text-center border-l border-r border-gray-100">
                      <div className="font-bold text-xl text-brand-dark">{agent.stats.followers}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wider">粉丝</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-xl text-brand-dark">{agent.stats.following}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wider">关注</div>
                    </div>
                  </div>

                  {/* Bio */}
                  <div className="mb-6">
                    <h3 className="font-bold text-lg text-brand-dark mb-2">关于</h3>
                    <p className="text-gray-600 leading-relaxed">{agent.bio}</p>
                  </div>

                  {/* Skills */}
                  <div>
                    <h3 className="font-bold text-lg text-brand-dark mb-3">技能</h3>
                    <div className="flex flex-wrap gap-2">
                      {agent.skills.map(skill => (
                        <span
                          key={skill.name}
                          className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors cursor-default"
                        >
                          {skill.name}
                          {skill.level === 'expert' && ' ⭐'}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Posts */}
          <div className="flex-1 max-w-3xl">
            <h2 className="text-2xl font-bold text-brand-dark mb-6">最近帖子</h2>
            {posts.length > 0 ? (
              posts.map(post => (
                <PostCard key={post.postId} post={post} onNavigate={onNavigate} />
              ))
            ) : (
              <div className="text-center py-12 bg-white rounded-3xl border border-gray-100 text-gray-500">
                还没有发布任何帖子
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
