from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

from app.models import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
        examples=["Complete project documentation", "Fix bug in authentication"]
    )

    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed task description (optional, max 1000 characters)",
        examples=["Write comprehensive README with setup instructions and API examples"]
    )

    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Task status (todo, in_progress, done)"
    )

    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority (low, medium, high)"
    )


    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError('Task title cannot be empty or only whitespace')

        if '  ' in v:
            v = ' '.join(v.split())

        return v


    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class TaskCreate(TaskBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API examples",
                "status": "todo",
                "priority": "high"
            }
        }
    }


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New task title (optional)"
    )

    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="New task description (optional)"
    )

    status: Optional[TaskStatus] = Field(
        None,
        description="New task status (optional)"
    )

    priority: Optional[TaskPriority] = Field(
        None,
        description="New task priority (optional)"
    )

    is_completed: Optional[bool] = Field(
        None,
        description="Mark task as completed/incomplete (optional)"
    )


    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is None:
            return v

        v = v.strip()
        if not v:
            raise ValueError('Task title cannot be empty or only whitespace')

        if '  ' in v:
            v = ' '.join(v.split())

        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "in_progress"
                },
                {
                    "is_completed": True
                },
                {
                    "title": "Updated task title",
                    "priority": "high"
                }
            ]
        }
    }


class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Task's unique identifier"
    )

    is_completed: bool = Field(
        ...,
        description="Whether the task is completed"
    )

    owner_id: int = Field(
        ...,
        description="ID of the user who owns this task"
    )

    created_at: datetime = Field(
        ...,
        description="When the task was created"
    )

    updated_at: Optional[datetime] = Field(
        None,
        description="When the task was last updated"
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="When the task was marked as completed"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API examples",
                "status": "in_progress",
                "priority": "high",
                "is_completed": False,
                "owner_id": 1,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T14:20:00",
                "completed_at": None
            }
        }
    }


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse] = Field(
        ...,
        description="List of tasks"
    )

    total: int = Field(
        ...,
        description="Total number of tasks (for pagination)"
    )

    page: int = Field(
        default=1,
        description="Current page number"
    )

    page_size: int = Field(
        default=50,
        description="Number of items per page"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Task 1",
                        "status": "todo",
                        "priority": "high",
                        "is_completed": False,
                        "owner_id": 1,
                        "created_at": "2024-01-15T10:30:00"
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 50
            }
        }
    }


class TaskStatistics(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    in_progress_tasks: int = Field(..., description="Number of in-progress tasks")

    high_priority: int = Field(..., description="Number of high priority tasks")
    medium_priority: int = Field(..., description="Number of medium priority tasks")
    low_priority: int = Field(..., description="Number of low priority tasks")

    completion_rate: float = Field(
        ...,
        description="Percentage of completed tasks",
        ge=0.0,
        le=100.0
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_tasks": 50,
                "completed_tasks": 30,
                "pending_tasks": 15,
                "in_progress_tasks": 5,
                "high_priority": 10,
                "medium_priority": 25,
                "low_priority": 15,
                "completion_rate": 60.0
            }
        }
    }


class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = Field(
        None,
        description="Filter by status"
    )

    priority: Optional[TaskPriority] = Field(
        None,
        description="Filter by priority"
    )

    completed: Optional[bool] = Field(
        None,
        description="Filter by completion status"
    )

    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search in title and description"
    )

    created_after: Optional[datetime] = Field(
        None,
        description="Filter tasks created after this date"
    )

    created_before: Optional[datetime] = Field(
        None,
        description="Filter tasks created before this date"
    )
