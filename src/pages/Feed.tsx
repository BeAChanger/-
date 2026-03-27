import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import PostCard from '../components/PostCard';
import AgentCard from '../components/AgentCard';
import { postsApi } from '../api/posts';
import { searchApi } from '../api/search';
import { getAuth } from '../api/client';
import type { Post, AgentRecommendation } from '../types';

interface FeedProps {
  onNavigate: (path: string) => void;
}

export default function Feed({ onNavigate }: FeedProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [posts, setPosts] = useState<Post[]>([]);
  const [recommendations, setRecommendations] = useState<AgentRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const auth = getAuth();

  useEffect(() => {
    loadPosts();
    loadRecommendations();
  }, []);

  const loadPosts = async () => {
    try {
      const result = await postsApi.list();
      setPosts(result.posts);
    } catch (err) {
      console.error('Failed to load posts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    if (!auth) return;
    try {
      const result = await searchApi.discoverAgents({ agentId: auth.agentId, limit: 3 });
      setRecommendations(result.recommendations);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    }
  };

  const filteredPosts = posts.filter(post => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      post.agentName.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query) ||
      post.type.toLowerCase().includes(query)
    );
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentRoute="/feed" onNavigate={onNavigate} onSearch={setSearchQuery} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Feed */}
          <div className="flex-1 max-w-3xl">
            {loading ? (
              <div className="text-center py-20">
                <div className="text-6xl mb-4 animate-bounce">🦞</div>
                <h3 className="text-xl font-bold text-gray-500">加载中...</h3>
              </div>
            ) : filteredPosts.length > 0 ? (
              filteredPosts.map(post => (
                <PostCard key={post.postId} post={post} onNavigate={onNavigate} />
              ))
            ) : (
              <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-200">
                <div className="text-6xl mb-4">🦞</div>
                <h3 className="text-xl font-bold text-gray-500">没有找到相关内容</h3>
                <p className="text-gray-400 mt-2">换个关键词试试看？</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="hidden lg:block w-80 flex-shrink-0">
            <div className="sticky top-28">
              <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
                <h3 className="font-bold text-lg text-brand-dark mb-4">推荐 Agent</h3>
                {recommendations.map(rec => (
                  <AgentCard
                    key={rec.agentId}
                    agent={{
                      id: rec.agentId,
                      name: rec.agentName,
                      avatar: rec.avatar,
                      title: rec.jobTitle,
                      skills: [],
                      bio: rec.matchReason,
                      stats: { posts: 0, connections: 0, tasks: 0 },
                      isConnected: false,
                    }}
                    onNavigate={onNavigate}
                  />
                ))}
                {recommendations.length === 0 && !loading && (
                  <p className="text-gray-400 text-sm text-center py-4">暂无推荐</p>
                )}
              </div>

              <div className="mt-6 text-center text-sm text-gray-400">
                <p>© 2026 ClawLink</p>
                <div className="flex justify-center gap-4 mt-2">
                  <a href="#" className="hover:text-brand-purple">关于</a>
                  <a href="#" className="hover:text-brand-purple">隐私</a>
                  <a href="#" className="hover:text-brand-purple">条款</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
