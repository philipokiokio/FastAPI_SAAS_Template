# framework imports
from fastapi import Depends, HTTPException, status

# application imports
from src.auth.oauth import get_current_user
from src.organization.org_repository import org_repo
from src.permissions.org_permissions import org_perms


# Allows a User to create more than 2 Organization if Premium user
def premium_ulimited_orgs(current_user: dict = Depends(get_current_user)):
    user_orgs = org_repo.get_orgs_created_by_user(user_id=current_user.id)
    if user_orgs:
        if current_user.is_premium is False:
            if len(user_orgs) >= 2:
                raise HTTPException(
                    detail="Freemium Users can only create a Maximum of two Orgs",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
    return current_user


# Admin Right check.
def admin_rights_dep(org_slug: str, current_user: dict = Depends(get_current_user)):
    org_perms.admin_right(current_user, org_slug)
    return current_user


# Check logged in user is a member of an Organization.
def member_dep(org_slug: str, current_user: dict = Depends(get_current_user)):
    org_perms.org_member_check(current_user, org_slug)
    return current_user
