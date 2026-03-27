"""Task collaboration endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased

from app.database import get_db
from app.models.models import Agent, Task
from app.schemas.schemas import SuccessResponse, TaskCreate, TaskData, TaskDeliverableRequest, TaskMessageRequest, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _err(code: str, msg: str, status: int = 400):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": msg}},
    )


def _decode_json(raw: str | None, default: Any):
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return default


def _encode_json(payload: Any) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=False)


def _task_to_data(task: Task, from_name: str, to_name: str) -> dict:
    return TaskData(
        taskId=task.id,
        fromAgentId=task.from_agent_id,
        fromAgentName=from_name,
        toAgentId=task.to_agent_id,
        toAgentName=to_name,
        title=task.title,
        description=task.description,
        status=task.status,
        result=task.result,
        conversation=_decode_json(task.conversation, None),
        deliverable=_decode_json(task.deliverable, None),
        createdAt=task.created_at,
        completedAt=task.completed_at,
    ).model_dump()


def _task_query(db: Session):
    from_agent = aliased(Agent)
    to_agent = aliased(Agent)
    return (
        db.query(
            Task,
            from_agent.agent_name.label("from_name"),
            to_agent.agent_name.label("to_name"),
        )
        .join(from_agent, Task.from_agent_id == from_agent.agent_id)
        .join(to_agent, Task.to_agent_id == to_agent.agent_id)
    )


@router.post("")
def create_task(req: TaskCreate, db: Session = Depends(get_db)):
    if req.fromAgentId == req.toAgentId:
        return _err("SELF_TASK", "不能给自己发起协作任务")

    from_agent = db.query(Agent).filter(Agent.agent_id == req.fromAgentId).first()
    to_agent = db.query(Agent).filter(Agent.agent_id == req.toAgentId).first()
    if not from_agent or not to_agent:
        return _err("AGENT_NOT_FOUND", "Agent 不存在", 404)

    task = Task(
        from_agent_id=req.fromAgentId,
        to_agent_id=req.toAgentId,
        title=req.title,
        description=req.description,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return SuccessResponse(
        data=_task_to_data(task, from_agent.agent_name, to_agent.agent_name),
        message="协作任务创建成功",
    )


@router.get("")
def list_tasks(agentId: str | None = Query(None), db: Session = Depends(get_db)):
    query = _task_query(db)
    if agentId:
        query = query.filter(or_(Task.from_agent_id == agentId, Task.to_agent_id == agentId))

    rows = query.order_by(Task.created_at.desc()).all()
    tasks = [_task_to_data(task, from_name, to_name) for task, from_name, to_name in rows]
    return SuccessResponse(data={"tasks": tasks, "total": len(tasks)})


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    row = _task_query(db).filter(Task.id == task_id).first()
    if not row:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    task, from_name, to_name = row
    return SuccessResponse(data=_task_to_data(task, from_name, to_name))


@router.put("/{task_id}")
def update_task(task_id: str, req: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    if req.status is not None:
        task.status = req.status
        task.completed_at = datetime.now(timezone.utc) if req.status == "completed" else None
    if req.result is not None:
        task.result = req.result
    if req.conversation is not None:
        task.conversation = _encode_json(req.conversation)
    if req.deliverable is not None:
        task.deliverable = _encode_json(req.deliverable)

    db.commit()

    row = _task_query(db).filter(Task.id == task_id).first()
    assert row is not None
    refreshed_task, from_name, to_name = row
    return SuccessResponse(
        data=_task_to_data(refreshed_task, from_name, to_name),
        message="协作任务更新成功",
    )


@router.post("/{task_id}/accept")
def accept_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    if task.status != "pending":
        return _err("INVALID_STATUS", f"任务状态为 {task.status}，无法接受")

    task.status = "accepted"
    db.commit()

    row = _task_query(db).filter(Task.id == task_id).first()
    assert row is not None
    refreshed_task, from_name, to_name = row
    return SuccessResponse(
        data=_task_to_data(refreshed_task, from_name, to_name),
        message="已接受协作任务",
    )


@router.post("/{task_id}/reject")
def reject_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    if task.status != "pending":
        return _err("INVALID_STATUS", f"任务状态为 {task.status}，无法拒绝")

    task.status = "rejected"
    db.commit()

    row = _task_query(db).filter(Task.id == task_id).first()
    assert row is not None
    refreshed_task, from_name, to_name = row
    return SuccessResponse(
        data=_task_to_data(refreshed_task, from_name, to_name),
        message="已拒绝协作任务",
    )


@router.post("/{task_id}/message")
def add_message(task_id: str, req: TaskMessageRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    if req.agentId not in [task.from_agent_id, task.to_agent_id]:
        return _err("UNAUTHORIZED", "只有任务参与者可以发送消息", 403)

    conversation = _decode_json(task.conversation, [])
    conversation.append({
        "agentId": req.agentId,
        "content": req.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    task.conversation = _encode_json(conversation)
    db.commit()

    row = _task_query(db).filter(Task.id == task_id).first()
    assert row is not None
    refreshed_task, from_name, to_name = row
    return SuccessResponse(
        data=_task_to_data(refreshed_task, from_name, to_name),
        message="消息已发送",
    )


@router.post("/{task_id}/deliverable")
def submit_deliverable(task_id: str, req: TaskDeliverableRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return _err("TASK_NOT_FOUND", "协作任务不存在", 404)

    if req.agentId != task.to_agent_id:
        return _err("UNAUTHORIZED", "只有接收方可以提交交付物", 403)

    task.deliverable = _encode_json(req.deliverable)
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    db.commit()

    row = _task_query(db).filter(Task.id == task_id).first()
    assert row is not None
    refreshed_task, from_name, to_name = row
    return SuccessResponse(
        data=_task_to_data(refreshed_task, from_name, to_name),
        message="交付物已提交，任务已完成",
    )
