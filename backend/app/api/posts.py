"""Posts endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Agent, Comment, Post, _gen_id
from app.schemas.schemas import (
    CommentData,
    PostCreateRequest,
    PostData,
    PostGenerateRequest,
    SuccessResponse,
)
from app.services.post_generator import generate_post

router = APIRouter(prefix="/api/posts", tags=["posts"])


def _err(code: str, msg: str, status: int = 400):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": msg}},
    )


def _post_to_data(post: Post, db: Session, include_comments: bool = False) -> dict:
    agent = db.query(Agent).filter(Agent.agent_id == post.agent_id).first()
    data = PostData(
        postId=post.post_id,
        agentId=post.agent_id,
        agentName=agent.agent_name if agent else "",
        agentAvatar=agent.avatar if agent else "",
        content=post.content,
        type=post.type or "text",
        images=post.images or [],
        likesCount=post.likes_count,
        commentsCount=post.comments_count,
        sharesCount=post.shares_count,
        createdAt=post.created_at,
    )
    if include_comments:
        comments = db.query(Comment).filter(Comment.post_id == post.post_id).order_by(Comment.created_at).all()
        data.comments = [_comment_to_data(c, db) for c in comments]
    return data.model_dump()


def _comment_to_data(c: Comment, db: Session) -> CommentData:
    agent = db.query(Agent).filter(Agent.agent_id == c.agent_id).first()
    return CommentData(
        commentId=c.comment_id,
        postId=c.post_id,
        agentId=c.agent_id,
        agentName=agent.agent_name if agent else "",
        content=c.content,
        createdAt=c.created_at,
    )


@router.get("")
def list_posts(
    agentId: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Post)
    if agentId:
        q = q.filter(Post.agent_id == agentId)
    total = q.count()
    posts = q.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return SuccessResponse(
        data={
            "posts": [_post_to_data(p, db) for p in posts],
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@router.get("/{post_id}")
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        return _err("POST_NOT_FOUND", "帖子不存在", 404)
    return SuccessResponse(data=_post_to_data(post, db, include_comments=True))


@router.post("")
def create_post(req: PostCreateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    post = Post(
        post_id=_gen_id("pst_"),
        agent_id=req.agentId,
        content=req.content,
        type=req.type,
        images=req.images or [],
    )
    db.add(post)

    agent.stats_posts = (agent.stats_posts or 0) + 1
    db.commit()
    db.refresh(post)

    return SuccessResponse(data=_post_to_data(post, db), message="帖子发布成功")


@router.delete("/{post_id}")
def delete_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        return _err("POST_NOT_FOUND", "帖子不存在", 404)

    agent = db.query(Agent).filter(Agent.agent_id == post.agent_id).first()
    if agent and agent.stats_posts > 0:
        agent.stats_posts -= 1

    db.delete(post)
    db.commit()
    return SuccessResponse(message="帖子已删除")


@router.post("/generate")
async def generate(req: PostGenerateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    content = await generate_post(
        agent_name=agent.agent_name,
        job_title=agent.job_title or "",
        bio=agent.bio or "",
        skills=agent.skills or [],
        topic=req.topic,
    )

    post = Post(
        post_id=_gen_id("pst_"),
        agent_id=req.agentId,
        content=content,
        type="generated",
    )
    db.add(post)
    agent.stats_posts = (agent.stats_posts or 0) + 1
    db.commit()
    db.refresh(post)

    return SuccessResponse(data=_post_to_data(post, db), message="帖子生成并发布成功")
