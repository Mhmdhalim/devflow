import uuid
from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.invitation import OrganizationInvitationRepository
from app.repositories.membership import MembershipRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.invitation import (
    OrganizationInvitationCreate,
    OrganizationInvitationCreated,
    OrganizationInvitationDetail,
    OrganizationInvitationRead,
    OrganizationMemberRead,
)
from app.schemas.organization import OrganizationMembershipRead
from app.services.organization_access import (
    OrganizationAccessNotFoundError,
    OrganizationAccessPermissionDeniedError,
    OrganizationAccessService,
    OrganizationInvitationAlreadyAcceptedError,
    OrganizationInvitationAlreadyExistsError,
    OrganizationInvitationEmailMismatchError,
    OrganizationInvitationExpiredError,
    OrganizationInvitationNotFoundError,
    OrganizationMemberAlreadyExistsError,
)

router = APIRouter(tags=["organization access"])


def get_organization_access_service(
    db: Session = Depends(get_db),
) -> OrganizationAccessService:
    return OrganizationAccessService(
        invitation_repository=OrganizationInvitationRepository(db),
        membership_repository=MembershipRepository(db),
        organization_repository=OrganizationRepository(db),
        user_repository=UserRepository(db),
    )


def _raise_invitation_error(exc: Exception) -> NoReturn:
    if isinstance(exc, OrganizationAccessNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        ) from exc

    if isinstance(exc, OrganizationAccessPermissionDeniedError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this organization",
        ) from exc

    if isinstance(exc, OrganizationMemberAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already a member of the organization",
        ) from exc

    if isinstance(exc, OrganizationInvitationAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending invitation already exists for this email",
        ) from exc

    if isinstance(exc, OrganizationInvitationNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        ) from exc

    if isinstance(exc, OrganizationInvitationExpiredError):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired",
        ) from exc

    if isinstance(exc, OrganizationInvitationAlreadyAcceptedError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation has already been accepted",
        ) from exc

    if isinstance(exc, OrganizationInvitationEmailMismatchError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation belongs to a different email address",
        ) from exc

    raise exc


@router.post(
    "/organizations/{organization_id}/invitations",
    response_model=OrganizationInvitationCreated,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    organization_id: uuid.UUID,
    data: OrganizationInvitationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: OrganizationAccessService = Depends(get_organization_access_service),
) -> OrganizationInvitationCreated:
    try:
        invitation, token = service.create_invitation(
            organization_id=organization_id,
            inviter_id=current_user.id,
            data=data,
        )
    except (
        OrganizationAccessNotFoundError,
        OrganizationAccessPermissionDeniedError,
        OrganizationMemberAlreadyExistsError,
        OrganizationInvitationAlreadyExistsError,
    ) as exc:
        _raise_invitation_error(exc)

    return OrganizationInvitationCreated(
        **OrganizationInvitationRead.model_validate(invitation).model_dump(),
        token=token,
    )


@router.get(
    "/organizations/{organization_id}/members",
    response_model=list[OrganizationMemberRead],
)
def list_members(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: OrganizationAccessService = Depends(get_organization_access_service),
) -> list[OrganizationMemberRead]:
    try:
        rows = service.list_members(
            organization_id=organization_id,
            user_id=current_user.id,
        )
    except (
        OrganizationAccessNotFoundError,
        OrganizationAccessPermissionDeniedError,
    ) as exc:
        _raise_invitation_error(exc)

    return [
        OrganizationMemberRead(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=membership.role,
            joined_at=membership.created_at,
        )
        for membership, user in rows
    ]


@router.get(
    "/organizations/{organization_id}/invitations",
    response_model=list[OrganizationInvitationRead],
)
def list_pending_invitations(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: OrganizationAccessService = Depends(get_organization_access_service),
) -> list[OrganizationInvitationRead]:
    try:
        invitations = service.list_pending_invitations(
            organization_id=organization_id,
            user_id=current_user.id,
        )
    except (
        OrganizationAccessNotFoundError,
        OrganizationAccessPermissionDeniedError,
    ) as exc:
        _raise_invitation_error(exc)

    return [
        OrganizationInvitationRead.model_validate(invitation)
        for invitation in invitations
    ]


@router.get(
    "/invitations/{token}",
    response_model=OrganizationInvitationDetail,
)
def get_invitation(
    token: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: OrganizationAccessService = Depends(get_organization_access_service),
) -> OrganizationInvitationDetail:
    try:
        invitation, organization = service.get_invitation(
            token=token,
            user_email=current_user.email,
        )
    except (
        OrganizationAccessNotFoundError,
        OrganizationInvitationNotFoundError,
        OrganizationInvitationExpiredError,
        OrganizationInvitationAlreadyAcceptedError,
        OrganizationInvitationEmailMismatchError,
    ) as exc:
        _raise_invitation_error(exc)

    return OrganizationInvitationDetail(
        **OrganizationInvitationRead.model_validate(invitation).model_dump(),
        organization_name=organization.name,
        organization_slug=organization.slug,
    )


@router.post(
    "/invitations/{token}/accept",
    response_model=OrganizationMembershipRead,
)
def accept_invitation(
    token: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: OrganizationAccessService = Depends(get_organization_access_service),
) -> OrganizationMembershipRead:
    try:
        organization, membership = service.accept_invitation(
            token=token,
            user=current_user,
        )
    except (
        OrganizationAccessNotFoundError,
        OrganizationInvitationNotFoundError,
        OrganizationInvitationExpiredError,
        OrganizationInvitationAlreadyAcceptedError,
        OrganizationInvitationEmailMismatchError,
        OrganizationMemberAlreadyExistsError,
    ) as exc:
        _raise_invitation_error(exc)

    return OrganizationMembershipRead(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        role=membership.role,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )
