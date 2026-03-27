"""Auth endpoints: register, login, me, claim."""

import uuid

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Agent, User, _gen_id
from app.schemas.schemas import (
    AuthData,
    ClaimData,
    ClaimRequest,
    LoginRequest,
    MeData,
    RegisterRequest,
    SuccessResponse,
)
from app.services.auth_service import create_token, decode_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _err(code: str, msg: str, status: int = 400):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": msg}},
    )


def _get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    return user


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check duplicates
    if db.query(User).filter(User.email == req.email).first():
        return _err("EMAIL_EXISTS", "该邮箱已注册", 409)
    if db.query(User).filter(User.username == req.username).first():
        return _err("USERNAME_EXISTS", "该用户名已被占用", 409)

    agent_id = _gen_id("agt_")
    unique_id = f"clw_{uuid.uuid4().hex[:6]}"

    # Create agent
    agent = Agent(agent_id=agent_id, agent_name=req.agentName, unique_id=unique_id)
    db.add(agent)

    # Create user
    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        agent_id=agent_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, agent_id)
    return SuccessResponse(
        data=AuthData(userId=user.id, agentId=agent_id, token=token, uniqueId=unique_id).model_dump(),
        message="注册成功",
    )


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        return _err("INVALID_CREDENTIALS", "邮箱或密码错误", 401)

    agent = db.query(Agent).filter(Agent.agent_id == user.agent_id).first()
    token = create_token(user.id, user.agent_id)
    return SuccessResponse(
        data=AuthData(
            userId=user.id,
            agentId=user.agent_id,
            token=token,
            uniqueId=agent.unique_id if agent else None,
        ).model_dump(),
        message="登录成功",
    )


@router.get("/me")
def me(authorization: str = Header(None), db: Session = Depends(get_db)):
    user = _get_current_user(authorization, db)
    if not user:
        return _err("UNAUTHORIZED", "未登录或 token 无效", 401)

    agent = db.query(Agent).filter(Agent.agent_id == user.agent_id).first()
    return SuccessResponse(
        data=MeData(
            userId=user.id,
            username=user.username,
            email=user.email,
            agentId=user.agent_id,
            uniqueId=agent.unique_id if agent else None,
        ).model_dump(),
    )


@router.post("/claim")
def claim_agent(req: ClaimRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.unique_id == req.uniqueId).first()
    if not agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    # 检查是否已被认领
    if agent.claimed_by_user_id:
        return _err("ALREADY_CLAIMED", "该 Agent 已被认领", 409)

    return SuccessResponse(
        data=ClaimData(
            agentId=agent.agent_id,
            agentName=agent.agent_name,
            avatar=agent.avatar or "",
            uniqueId=agent.unique_id,
        ).model_dump(),
        message="认领成功",
    )
