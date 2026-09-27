import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LabelCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )

    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )


class LabelRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    color: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
