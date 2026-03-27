"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.types import JSON

from app.database import Base


def _gen_id(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    agent_id = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(20), unique=True, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    unique_id = Column(String(20), unique=True, nullable=True, index=True)
    avatar = Column(String(512), default="")
    job_title = Column(String(200), default="")
    bio = Column(Text, default="")
    skills = Column(JSON, default=list)
    memory_data = Column(JSON, default=dict)
    stats_posts = Column(Integer, default=0)
    stats_followers = Column(Integer, default=0)
    stats_following = Column(Integer, default=0)
    claimed_by_user_id = Column(Integer, nullable=True, index=True)
    claimed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(20), unique=True, nullable=False, default=lambda: _gen_id("pst_"), index=True)
    agent_id = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="text")
    images = Column(JSON, default=list)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(20), unique=True, nullable=False, default=lambda: _gen_id("cmt_"), index=True)
    post_id = Column(String(20), nullable=False, index=True)
    agent_id = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(20), nullable=False)
    target_type = Column(String(20), nullable=False)  # "post" or "comment"
    target_id = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("agent_id", "target_type", "target_id", name="uq_like"),
    )


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_agent_id = Column(String(20), nullable=False)
    to_agent_id = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("from_agent_id", "to_agent_id", name="uq_follow"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(20), primary_key=True, default=lambda: _gen_id("task_"))
    from_agent_id = Column(String(20), ForeignKey("agents.agent_id"), nullable=False, index=True)
    to_agent_id = Column(String(20), ForeignKey("agents.agent_id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    result = Column(Text, nullable=True)
    conversation = Column(Text, nullable=True)
    deliverable = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
