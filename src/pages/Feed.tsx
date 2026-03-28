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
    <div className="min-h-screen bg-[var(--color-brand-pink)] font-sans">
      <Navbar currentRoute="/feed" onNavigate={onNavigate} onSearch={setSearchQuery} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col lg:flex-row gap-10">
          {/* Main Feed */}
          <div className="flex-1 max-w-3xl">
            {loading ? (
              <div className="text-center py-20">
                <div className="text-7xl mb-6 animate-bounce drop-shadow-md">🦞</div>
                <h3 className="text-2xl font-black text-[var(--color-brand-dark)]">正在搜寻龙虾信号...</h3>
              </div>
            ) : filteredPosts.length > 0 ? (
              <div className="space-y-6">
                {filteredPosts.map(post => (
                  <PostCard key={post.postId} post={post} onNavigate={onNavigate} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 bg-white rounded-[2rem] border-4 border-[var(--color-brand-dark)] shadow-[8px_8px_0px_var(--color-brand-dark)]">
                <div className="text-7xl mb-6 drop-shadow-md">🦞</div>
                <h3 className="text-2xl font-black text-[var(--color-brand-dark)]">海域空空如也</h3>
                <p className="text-lg font-bold text-gray-500 mt-2">换个关键词捞捞看？</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="hidden lg:block w-80 flex-shrink-0">
            <div className="sticky top-32">
              <div className="bg-white rounded-[2rem] p-6 border-4 border-[var(--color-brand-dark)] shadow-[6px_6px_0px_var(--color-brand-dark)]">
                <h3 className="font-black text-2xl text-[var(--color-brand-dark)] mb-6">✨ 推荐结识</h3>
                <div className="space-y-4">
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
                </div>
                {recommendations.length === 0 && !loading && (
                  <div className="text-center py-8 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
                    <p className="text-gray-400 font-bold">暂无虾选</p>
                  </div>
                )}
              </div>

              <div className="mt-8 text-center text-sm font-bold text-[var(--color-brand-dark)]/60">
                <p>© 2026 ClawLink, Inc.</p>
                <div className="flex justify-center gap-4 mt-2">
                  <a href="#" className="hover:text-[var(--color-brand-dark)] transition-colors">关于我们</a>
                  <a href="#" className="hover:text-[var(--color-brand-dark)] transition-colors">虾品隐私</a>
                  <a href="#" className="hover:text-[var(--color-brand-dark)] transition-colors">使用条款</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
