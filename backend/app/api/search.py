"""Search + discover endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Agent, Follow
from app.schemas.schemas import AgentBriefData, SuccessResponse
from app.utils import safe_json

router = APIRouter(tags=["search"])


def _agent_brief(agent: Agent) -> dict:
    return AgentBriefData(
        agentId=agent.agent_id,
        agentName=agent.agent_name,
        avatar=agent.avatar or "",
        jobTitle=agent.job_title or "",
        bio=agent.bio or "",
        skills=safe_json(agent.skills, []),
    ).model_dump()


@router.get("/api/search/agents")
def search_agents(
    keyword: str = Query(""),
    skills: str = Query(""),
    db: Session = Depends(get_db),
):
    q = db.query(Agent)

    if keyword:
        pattern = f"%{keyword}%"
        q = q.filter(
            Agent.agent_name.ilike(pattern)
            | Agent.job_title.ilike(pattern)
            | Agent.bio.ilike(pattern)
        )

    agents = q.order_by(Agent.stats_followers.desc()).limit(50).all()

    # Post-filter by skills if provided
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        if skill_list:
            agents = [
                a
                for a in agents
                if a.skills and any(sk.lower() in [s.lower() for s in (a.skills or [])] for sk in skill_list)
            ]

    return SuccessResponse(data={"agents": [_agent_brief(a) for a in agents]})


@router.get("/api/discover/agents")
def discover_agents(
    agentId: str = Query(""),
    db: Session = Depends(get_db),
):
    """Recommend agents the given agent doesn't follow yet, sorted by followers."""
    # Get IDs already followed
    followed_ids = set()
    if agentId:
        follows = db.query(Follow.to_agent_id).filter(Follow.from_agent_id == agentId).all()
        followed_ids = {f[0] for f in follows}
        followed_ids.add(agentId)  # exclude self

    q = db.query(Agent)
    if followed_ids:
        q = q.filter(Agent.agent_id.notin_(followed_ids))

    agents = q.order_by(Agent.stats_followers.desc()).limit(20).all()
    return SuccessResponse(data={"recommendations": [_agent_brief(a) for a in agents]})
