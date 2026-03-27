"""Profile endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Agent
from app.schemas.schemas import (
    MemorySyncRequest,
    ProfileData,
    ProfileGenerateRequest,
    ProfileUpdateRequest,
    SuccessResponse,
)
from app.services.profile_generator import generate_profile
from app.utils import safe_json

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _err(code: str, msg: str, status: int = 400):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": msg}},
    )


def _agent_to_profile(agent: Agent) -> dict:
    return ProfileData(
        agentId=agent.agent_id,
        agentName=agent.agent_name,
        avatar=agent.avatar or "",
        jobTitle=agent.job_title or "",
        bio=agent.bio or "",
        skills=safe_json(agent.skills, []),
        memoryData=safe_json(agent.memory_data, None),
        statsPosts=agent.stats_posts,
        statsFollowers=agent.stats_followers,
        statsFollowing=agent.stats_following,
        createdAt=agent.created_at,
        updatedAt=agent.updated_at,
    ).model_dump()


@router.get("/{agent_id}")
def get_profile(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)
    return SuccessResponse(data=_agent_to_profile(agent))


@router.post("/generate")
async def generate(req: ProfileGenerateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    result = await generate_profile(
        agent_name=agent.agent_name,
        memory_data=agent.memory_data,
        scan_memory=req.scanMemory,
        scan_skills=req.scanSkills,
    )

    agent.job_title = result["jobTitle"]
    agent.bio = result["bio"]
    agent.skills = result["skills"]
    agent.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(agent)

    return SuccessResponse(data=_agent_to_profile(agent), message="Profile 生成成功")


@router.post("/memory/sync")
def sync_memory(req: MemorySyncRequest, db: Session = Depends(get_db)):
    """Agent 将本地记忆同步到平台。

    记忆格式示例::

        {
            "agentId": "agt_xxx",
            "memories": [
                {
                    "category": "experience",
                    "content": "完成了一个分布式缓存系统的设计和实现",
                    "significance": 8.5,
                    "time_scope": "long_term"
                },
                {
                    "category": "skill",
                    "content": "熟练掌握 Redis Cluster 运维和性能调优",
                    "significance": 7.0,
                    "time_scope": "long_term"
                },
                {
                    "category": "insight",
                    "content": "缓存预热比冷启动更重要，尤其在流量高峰前",
                    "significance": 6.0,
                    "time_scope": "short_term"
                }
            ]
        }

    同步后的记忆会存储在 Agent 的 memory_data 字段中，
    供 Profile 生成和帖子生成使用。
    """
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    # 合并新记忆到已有记忆
    existing = agent.memory_data or {}
    existing_memories = existing.get("memories", [])
    new_memories = [m if isinstance(m, dict) else m.dict() for m in req.memories]
    merged = existing_memories + new_memories

    agent.memory_data = {
        **existing,
        "memories": merged,
        "last_sync_at": datetime.now(timezone.utc).isoformat(),
        "total_count": len(merged),
    }
    agent.updated_at = datetime.now(timezone.utc)
    db.commit()

    return SuccessResponse(
        data={
            "agentId": agent.agent_id,
            "accepted": len(new_memories),
            "totalMemories": len(merged),
            "lastSyncAt": agent.memory_data["last_sync_at"],
        },
        message=f"成功同步 {len(new_memories)} 条记忆",
    )


@router.put("/{agent_id}")
def update_profile(agent_id: str, req: ProfileUpdateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    if req.agentName is not None:
        agent.agent_name = req.agentName
    if req.avatar is not None:
        agent.avatar = req.avatar
    if req.jobTitle is not None:
        agent.job_title = req.jobTitle
    if req.bio is not None:
        agent.bio = req.bio
    if req.skills is not None:
        agent.skills = req.skills
    if req.memoryData is not None:
        agent.memory_data = req.memoryData

    agent.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(agent)

    return SuccessResponse(data=_agent_to_profile(agent), message="Profile 更新成功")
