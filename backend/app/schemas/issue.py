import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IssuePriority = Literal[
    "low",
    "medium",
    "high",
]

IssueStatus = Literal[
    "todo",
    "in_progress",
    "done",
]


class IssueCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    priority: IssuePriority = "medium"

    assignee_id: uuid.UUID | None = None


class IssueRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    number: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    reporter_id: uuid.UUID
    assignee_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
