from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies import get_current_active_user
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Task:
    task = Task(**task_data.model_dump(), owner_id=current_user.id)

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    completed: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Task]:
    query = select(Task).where(Task.owner_id == current_user.id)

    if status_filter:
        query = query.where(Task.status == status_filter)

    if priority_filter:
        query = query.where(Task.priority == priority_filter)

    if completed is not None:
        query = query.where(Task.is_completed == completed)

    query = query.order_by(Task.created_at.desc())

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundException("Task not found")

    if task.owner_id != current_user.id:
        raise ForbiddenException("Not authorized to access this task")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundException("Task not found")

    if task.owner_id != current_user.id:
        raise ForbiddenException("Not authorized to update this task")

    update_data = task_update.model_dump(exclude_unset=True)

    if "is_completed" in update_data and update_data["is_completed"]:
        update_data["completed_at"] = datetime.utcnow()
        update_data["status"] = TaskStatus.DONE
    elif "is_completed" in update_data and not update_data["is_completed"]:
        update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundException("Task not found")

    if task.owner_id != current_user.id:
        raise ForbiddenException("Not authorized to delete this task")

    await db.delete(task)
    await db.commit()

    return None
