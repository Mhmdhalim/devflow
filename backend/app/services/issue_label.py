import uuid

from app.models.issue import Issue
from app.models.label import Label
from app.repositories.issue import IssueRepository
from app.repositories.label import LabelRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository


class IssueLabelProjectNotFoundError(Exception):
    pass


class IssueLabelPermissionDeniedError(Exception):
    pass


class IssueLabelIssueNotFoundError(Exception):
    pass


class IssueLabelLabelNotFoundError(Exception):
    pass


class IssueLabelLabelProjectMismatchError(Exception):
    pass


class IssueLabelAlreadyAssignedError(Exception):
    pass


class IssueLabelNotAssignedError(Exception):
    pass


class IssueLabelService:
    def __init__(
        self,
        label_repository: LabelRepository,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self.label_repository = label_repository
        self.issue_repository = issue_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _get_issue_for_member(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        user_id: uuid.UUID,
    ) -> Issue:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise IssueLabelProjectNotFoundError

        membership = self.membership_repository.get_for_user_and_organization(
            user_id=user_id,
            organization_id=project.organization_id,
        )

        if membership is None:
            raise IssueLabelPermissionDeniedError

        issue = self.issue_repository.get_by_number(
            project_id=project_id,
            issue_number=issue_number,
        )

        if issue is None:
            raise IssueLabelIssueNotFoundError

        return issue

    def _get_label_for_project(
        self,
        label_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> Label:
        label = self.label_repository.get_by_id(label_id)

        if label is None:
            raise IssueLabelLabelNotFoundError

        if label.project_id != project_id:
            raise IssueLabelLabelProjectMismatchError

        return label

    def assign_label(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        label_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Label:
        issue = self._get_issue_for_member(
            project_id=project_id,
            issue_number=issue_number,
            user_id=user_id,
        )

        label = self._get_label_for_project(
            label_id=label_id,
            project_id=project_id,
        )

        if self.label_repository.is_assigned_to_issue(
            issue_id=issue.id,
            label_id=label_id,
        ):
            raise IssueLabelAlreadyAssignedError

        self.label_repository.assign_to_issue(
            issue_id=issue.id,
            label_id=label_id,
        )

        return label

    def remove_label(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        label_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        issue = self._get_issue_for_member(
            project_id=project_id,
            issue_number=issue_number,
            user_id=user_id,
        )

        self._get_label_for_project(
            label_id=label_id,
            project_id=project_id,
        )

        if not self.label_repository.is_assigned_to_issue(
            issue_id=issue.id,
            label_id=label_id,
        ):
            raise IssueLabelNotAssignedError

        self.label_repository.remove_from_issue(
            issue_id=issue.id,
            label_id=label_id,
        )

    def list_labels(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        user_id: uuid.UUID,
    ) -> list[Label]:
        issue = self._get_issue_for_member(
            project_id=project_id,
            issue_number=issue_number,
            user_id=user_id,
        )

        return self.label_repository.list_for_issue(issue.id)
