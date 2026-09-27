import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )
    slug: str = Field(
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class OrganizationRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationMembershipRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    role: str
    created_at: datetime
    updated_at: datetime
