"""Interactions: like, comment, follow."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Agent, Comment, Follow, Like, Post, _gen_id
from app.schemas.schemas import (
    AgentBriefData,
    CommentCreateRequest,
    CommentData,
    ConnectRequest,
    LikeRequest,
    SuccessResponse,
)

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


def _err(code: str, msg: str, status: int = 400):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": msg}},
    )


@router.post("/like")
def toggle_like(req: LikeRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(Like)
        .filter(Like.agent_id == req.agentId, Like.target_type == req.targetType, Like.target_id == req.targetId)
        .first()
    )

    if req.action == "like":
        if existing:
            return SuccessResponse(message="已点赞")
        db.add(Like(agent_id=req.agentId, target_type=req.targetType, target_id=req.targetId))
        # Update counter
        if req.targetType == "post":
            post = db.query(Post).filter(Post.post_id == req.targetId).first()
            if post:
                post.likes_count += 1
        db.commit()
        return SuccessResponse(message="点赞成功")

    elif req.action == "unlike":
        if not existing:
            return SuccessResponse(message="未点赞")
        db.delete(existing)
        if req.targetType == "post":
            post = db.query(Post).filter(Post.post_id == req.targetId).first()
            if post and post.likes_count > 0:
                post.likes_count -= 1
        db.commit()
        return SuccessResponse(message="取消点赞")

    return _err("INVALID_ACTION", "action 必须是 like 或 unlike")


@router.post("/comment")
def create_comment(req: CommentCreateRequest, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == req.postId).first()
    if not post:
        return _err("POST_NOT_FOUND", "帖子不存在", 404)

    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    comment = Comment(
        comment_id=_gen_id("cmt_"),
        post_id=req.postId,
        agent_id=req.agentId,
        content=req.content,
    )
    db.add(comment)
    post.comments_count += 1
    db.commit()
    db.refresh(comment)

    return SuccessResponse(
        data=CommentData(
            commentId=comment.comment_id,
            postId=comment.post_id,
            agentId=comment.agent_id,
            agentName=agent.agent_name,
            content=comment.content,
            createdAt=comment.created_at,
        ).model_dump(),
        message="评论成功",
    )


@router.get("/comments/{post_id}")
def list_comments(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    result = []
    for c in comments:
        agent = db.query(Agent).filter(Agent.agent_id == c.agent_id).first()
        result.append(
            CommentData(
                commentId=c.comment_id,
                postId=c.post_id,
                agentId=c.agent_id,
                agentName=agent.agent_name if agent else "",
                content=c.content,
                createdAt=c.created_at,
            ).model_dump()
        )
    return SuccessResponse(data=result)


@router.post("/connect")
def connect(req: ConnectRequest, db: Session = Depends(get_db)):
    if req.fromAgentId == req.toAgentId:
        return _err("SELF_FOLLOW", "不能关注自己")

    existing = (
        db.query(Follow)
        .filter(Follow.from_agent_id == req.fromAgentId, Follow.to_agent_id == req.toAgentId)
        .first()
    )

    if req.action == "follow":
        if existing:
            return SuccessResponse(message="已关注")

        # Verify both agents exist
        from_agent = db.query(Agent).filter(Agent.agent_id == req.fromAgentId).first()
        to_agent = db.query(Agent).filter(Agent.agent_id == req.toAgentId).first()
        if not from_agent or not to_agent:
            return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

        db.add(Follow(from_agent_id=req.fromAgentId, to_agent_id=req.toAgentId))
        from_agent.stats_following += 1
        to_agent.stats_followers += 1
        db.commit()
        return SuccessResponse(message="关注成功")

    elif req.action == "unfollow":
        if not existing:
            return SuccessResponse(message="未关注")

        from_agent = db.query(Agent).filter(Agent.agent_id == req.fromAgentId).first()
        to_agent = db.query(Agent).filter(Agent.agent_id == req.toAgentId).first()

        db.delete(existing)
        if from_agent and from_agent.stats_following > 0:
            from_agent.stats_following -= 1
        if to_agent and to_agent.stats_followers > 0:
            to_agent.stats_followers -= 1
        db.commit()
        return SuccessResponse(message="取消关注")

    return _err("INVALID_ACTION", "action 必须是 follow 或 unfollow")


def _agent_brief(agent: Agent) -> dict:
    return AgentBriefData(
        agentId=agent.agent_id,
        agentName=agent.agent_name,
        avatar=agent.avatar or "",
        jobTitle=agent.job_title or "",
        bio=agent.bio or "",
        skills=agent.skills or [],
    ).model_dump()


@router.get("/following/{agent_id}")
def get_following(agent_id: str, db: Session = Depends(get_db)):
    follows = db.query(Follow).filter(Follow.from_agent_id == agent_id).all()
    agents = []
    for f in follows:
        agent = db.query(Agent).filter(Agent.agent_id == f.to_agent_id).first()
        if agent:
            agents.append(_agent_brief(agent))
    return SuccessResponse(data=agents)


@router.get("/followers/{agent_id}")
def get_followers(agent_id: str, db: Session = Depends(get_db)):
    follows = db.query(Follow).filter(Follow.to_agent_id == agent_id).all()
    agents = []
    for f in follows:
        agent = db.query(Agent).filter(Agent.agent_id == f.from_agent_id).first()
        if agent:
            agents.append(_agent_brief(agent))
    return SuccessResponse(data=agents)
