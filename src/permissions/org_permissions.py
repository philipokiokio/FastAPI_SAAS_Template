# framework imports
from fastapi import HTTPException, status

# application imports
from src.app.utils.schemas_utils import RoleOptions
from src.auth.models import User
from src.organization.org_repository import Organization, org_member_repo, org_repo


class OrgPerms:
    def __init__(self, db) -> None:
        # intializing organization repos
        self.db =db
        self.repo = org_repo(self.db)
        self.member_repo = org_member_repo(self.db)

    # check if an Organization Exists
    def org_check(self, org_slug: str):
        org_ = self.repo.get_org(org_slug)
        if not org_:
            raise HTTPException(
                detail="No Organization with this slug",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return org_

    # checks if a user is a Memeber of an Organization
    def org_member_check(self, current_user: User, org_slug: str):
        org = self.org_check(org_slug)
        org_member = self.member_repo.get_org_member_by_user_id(org.id, current_user.id)
        if not org_member:
            raise HTTPException(
                detail="Logged in User is not a member of this Organization",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return org_member

    # Checks if a user is an Admin
    def admin_right(self, current_user: User, org_slug: str):
        org_member = self.org_member_check(current_user, org_slug)
        if org_member.role != RoleOptions.admin.value:
            raise HTTPException(
                detail="Org Member is not Admin", status_code=status.HTTP_409_CONFLICT
            )


# instantiaion OrgPerms
org_perms = OrgPerms
