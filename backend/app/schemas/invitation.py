import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

InvitationRole = Literal["admin", "member"]


class OrganizationInvitationCreate(BaseModel):
    email: EmailStr
    role: InvitationRole = "member"


class OrganizationInvitationRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: InvitationRole
    invited_by_id: uuid.UUID
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationInvitationCreated(OrganizationInvitationRead):
    token: str


class OrganizationInvitationDetail(OrganizationInvitationRead):
    organization_name: str
    organization_slug: str


class OrganizationMemberRead(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    joined_at: datetime
