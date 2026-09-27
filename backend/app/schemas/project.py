import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=1,
        max_length=120,
    )

    key: str = Field(
        min_length=1,
        max_length=20,
        pattern=r"^[A-Z][A-Z0-9]*$",
    )

    description: str | None = None


class ProjectRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    key: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
