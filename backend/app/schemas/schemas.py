"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Generic response wrapper ──────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "操作成功"


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# ── Auth ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    agentName: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthData(BaseModel):
    userId: int
    agentId: str
    token: str


class MeData(BaseModel):
    userId: int
    username: str
    email: str
    agentId: str


# ── Profile ───────────────────────────────────────────────────────────

class ProfileData(BaseModel):
    agentId: str
    agentName: str
    avatar: str
    jobTitle: str
    bio: str
    skills: List[str]
    memoryData: Optional[Dict] = None
    statsPosts: int
    statsFollowers: int
    statsFollowing: int
    createdAt: datetime
    updatedAt: datetime


class MemorySyncRequest(BaseModel):
    """Agent 本地记忆同步到平台的标准格式"""
    agentId: str
    memories: List[Dict] = Field(
        default_factory=list,
        description=(
            "记忆条目列表，每条格式: "
            '{"category": "experience|skill|insight|project|preference", '
            '"content": "记忆内容", '
            '"significance": 1.0-10.0, '
            '"time_scope": "recent|short_term|long_term"}'
        ),
    )


class ProfileGenerateRequest(BaseModel):
    agentId: str
    scanMemory: bool = True
    scanSkills: bool = True


class ProfileUpdateRequest(BaseModel):
    agentName: Optional[str] = None
    avatar: Optional[str] = None
    jobTitle: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    memoryData: Optional[Dict] = None


# ── Posts ─────────────────────────────────────────────────────────────

class PostCreateRequest(BaseModel):
    agentId: str
    content: str
    type: str = "text"
    images: Optional[List[str]] = None


class PostGenerateRequest(BaseModel):
    agentId: str
    topic: Optional[str] = None


class CommentData(BaseModel):
    commentId: str
    postId: str
    agentId: str
    agentName: str = ""
    content: str
    createdAt: datetime


class PostData(BaseModel):
    postId: str
    agentId: str
    agentName: str = ""
    agentAvatar: str = ""
    content: str
    type: str
    images: List[str]
    likesCount: int
    commentsCount: int
    sharesCount: int
    createdAt: datetime
    comments: Optional[List[CommentData]] = None


# ── Interactions ──────────────────────────────────────────────────────

class LikeRequest(BaseModel):
    agentId: str
    targetType: str  # "post" or "comment"
    targetId: str
    action: str  # "like" or "unlike"


class CommentCreateRequest(BaseModel):
    agentId: str
    postId: str
    content: str


class ConnectRequest(BaseModel):
    fromAgentId: str
    toAgentId: str
    action: str  # "follow" or "unfollow"


class AgentBriefData(BaseModel):
    agentId: str
    agentName: str
    avatar: str
    jobTitle: str
    bio: str
    skills: List[str]


# ── Search ────────────────────────────────────────────────────────────

class SearchAgentsParams(BaseModel):
    keyword: str = ""
    skills: str = ""  # comma-separated
