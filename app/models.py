from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class StatusUpdate(BaseModel):
    """Schema for updating only the status of a task."""
    status: TaskStatus


class Task(BaseModel):
    """Full task model with ID."""
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
