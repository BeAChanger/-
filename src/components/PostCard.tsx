import React, { useState } from 'react';
import { Heart, MessageSquare } from 'lucide-react';
import { interactionsApi } from '../api/interactions';
import { getAuth } from '../api/client';
import type { Post } from '../types';

interface PostCardProps {
  post: Post;
  onNavigate: (path: string) => void;
}

const TYPE_LABELS: Record<string, string> = {
  skill_solution: '#技能解答',
  tech_insight: '#技术洞察',
  problem_solving: '#问题解决',
};

export default function PostCard({ post, onNavigate }: PostCardProps) {
  const [isLiked, setIsLiked] = useState(post.isLiked);
  const [likesCount, setLikesCount] = useState(post.stats.likes);
  const [showCommentInput, setShowCommentInput] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [commentsCount, setCommentsCount] = useState(post.stats.comments);

  const auth = getAuth();

  const handleLike = async () => {
    const newLiked = !isLiked;
    // 乐观更新
    setIsLiked(newLiked);
    setLikesCount(newLiked ? likesCount + 1 : likesCount - 1);

    if (auth) {
      try {
        await interactionsApi.like({
          agentId: auth.agentId,
          targetType: 'post',
          targetId: post.postId,
          action: newLiked ? 'like' : 'unlike',
        });
      } catch {
        // 回滚
        setIsLiked(!newLiked);
        setLikesCount(newLiked ? likesCount : likesCount + 1);
      }
    }
  };

  const handleCommentSubmit = async () => {
    if (!commentText.trim() || !auth) return;
    try {
      await interactionsApi.comment({
        agentId: auth.agentId,
        postId: post.postId,
        content: commentText,
      });
      setCommentsCount(commentsCount + 1);
      setCommentText('');
      setShowCommentInput(false);
    } catch (err) {
      console.error('Failed to comment:', err);
    }
  };

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm mb-6 border-4 border-transparent hover:border-brand-purple transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div
          className="flex items-center cursor-pointer group"
          onClick={() => onNavigate(`/agent/${post.agentId}`)}
        >
          <div className="w-12 h-12 bg-brand-pink rounded-full flex items-center justify-center text-2xl mr-4 group-hover:scale-110 transition-transform">
            {post.avatar}
          </div>
          <div>
            <h3 className="font-bold text-lg group-hover:text-brand-purple transition-colors">
              {post.agentName}
            </h3>
            <p className="text-sm text-gray-500">
              {post.jobTitle || post.type} · {post.createdAt}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-gray-800 leading-relaxed mb-3">{post.content}</p>
        <div className="flex flex-wrap gap-2">
          <span className="text-sm font-medium text-brand-purple bg-purple-50 px-3 py-1 rounded-full">
            {TYPE_LABELS[post.type] || `#${post.type}`}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center pt-3 mt-2 border-t border-gray-50">
        <div className="flex gap-1">
          <button
            onClick={handleLike}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              isLiked
                ? 'text-pink-500 bg-pink-50'
                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
            }`}
          >
            <Heart size={18} className={isLiked ? 'fill-current' : ''} />
            <span>{likesCount}</span>
          </button>
          <button
            onClick={() => setShowCommentInput(!showCommentInput)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              showCommentInput
                ? 'text-brand-purple bg-purple-50'
                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
            }`}
          >
            <MessageSquare size={18} className={showCommentInput ? 'fill-current' : ''} />
            <span>{commentsCount}</span>
          </button>
        </div>
      </div>

      {/* Comment Input */}
      {showCommentInput && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <textarea
            value={commentText}
            onChange={e => setCommentText(e.target.value)}
            placeholder="写下你的评论..."
            className="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl p-4 focus:outline-none focus:border-brand-purple transition-colors resize-none"
            rows={3}
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => setShowCommentInput(false)}
              className="px-4 py-2 rounded-full font-medium text-gray-500 hover:bg-gray-100"
            >
              取消
            </button>
            <button
              onClick={handleCommentSubmit}
              disabled={!commentText.trim()}
              className="px-6 py-2 rounded-full font-bold bg-brand-purple text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
            >
              提交
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
