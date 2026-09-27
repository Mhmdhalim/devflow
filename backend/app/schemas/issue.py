import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    priority: IssuePriority = "medium"

    assignee_id: uuid.UUID | None = None


class IssueUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    assignee_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(
        self,
    ) -> "IssueUpdate":
        for field_name in (
            "title",
            "status",
            "priority",
        ):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null")

        return self


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
