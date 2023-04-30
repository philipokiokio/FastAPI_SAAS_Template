# framework import
from fastapi import APIRouter, Depends, status

# application imports
from src.auth.models import User
from src.auth.oauth import get_current_user
from src.organization import schemas
from src.organization.org_service import org_service
from src.organization.pipes import org_dep
from src.app.utils.db_utils import get_db
from sqlalchemy.orm import Session


# org router
org_router = APIRouter(prefix="/api/v1/org", tags=["Organization and Org Members"])


@org_router.post(
    "/create/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MessageOrgResp,
)
def create_org(
    create_workspace: schemas.OrgCreate,
    current_user: User = Depends(org_dep.premium_ulimited_orgs),db:Session = Depends(get_db)
):
    """Create Org

    Args:
        create_workspace (schemas.OrgCreate): data
        current_user (User, optional): _description_. Defaults to Depends(org_dep.premium_ulimited_orgs): Premium check.

    Returns:
        _type_: Resp
    """
    resp = org_service(db).create_org(current_user.id, create_workspace)

    return resp


@org_router.get(
    "s/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageListOrgResp,
)
def get_orgs(current_user: User = Depends(get_current_user),db:Session = Depends(get_db)):
    """Get Orgs

    Args:
        current_user (User, optional): _description_. Defaults to Depends(get_current_user): Logged in User.

    Returns:
        _type_: resp
    """
    resp = org_service(db).get_user_org(current_user.id)

    return resp


@org_router.get(
    "/{org_slug}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgResp,
)
def get_org(org_slug: str, current_user: User = Depends(org_dep.member_dep),db:Session = Depends(get_db)):
    """Get Org

    Args:
        org_slug (str): slug
        current_user (User, optional): _description_. Defaults to Depends(org_dep.member_dep): Logged in Org Member

    Returns:
        _type_: resp
    """
    resp = org_service(db).get_org(org_slug)

    return resp


@org_router.patch(
    "/{org_slug}/update/",
    response_model=schemas.MessageOrgResp,
    status_code=status.HTTP_200_OK,
)
def org_update(
    org_slug: str,
    update_org: schemas.OrgUpdate,
    current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)
):
    """Org Update

    Args:
        org_slug (str): Slug
        update_org (schemas.OrgUpdate): Data
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep): Loggeed inn userr with write access.

    Returns:
        _type_: resp
    """
    resp = org_service(db).update_org(org_slug, update_org)

    return resp


@org_router.delete(
    "/{org_slug}/delete/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def org_delete(org_slug: str, current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)):
    """Delete Organization

    Args:
        org_slug (str): Slug
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep)= Write access.

    Returns:
        _type_: 204
    """
    org_service(db).delete_org(org_slug)

    return {"status": status.HTTP_204_NO_CONTENT}


@org_router.post(
    "/{org_slug}/invite-link/gen/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InviteOrgResponse,
)
def generate_org_invite_link(
    org_slug: str,
    role_data: schemas.UpdateOrgMember,
    current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)
):
    """GENERATE ORG LINK

    Args:
        org_slug (str): str
        role_data (schemas.UpdateOrgMember): role information
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep).

    Returns:
        _type_: resp
    """
    resp = org_service(db).org_link_invite(org_slug, role_data.role)

    return resp


@org_router.post(
    "/{org_slug}/revoke-link/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgResp,
)
def revoke_org(org_slug: str, current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)):
    """Revoke Org Access

    Args:
        org_slug (str): slug
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep): Logged in user with right access.

    Returns:
        _type_: resp
    """
    resp = org_service(db).revoke_org_link(org_slug)
    return resp


@org_router.post(
    "/join/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgMembResp,
)
def org_member_join(token: str, role_token: str, new_org_member: schemas.JoinOrg,db:Session = Depends(get_db)):
    """Join Org

    Args:
        token (str): str
        role_token (str): role token
        new_org_member (schemas.JoinOrg): data

    Returns:
        _type_: resp
    """
    resp = org_service(db).join_org(token, role_token, new_org_member)

    return resp


@org_router.get(
    "/{org_slug}/member/{member_id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgMembResp,
)
def get_org_member(
    org_slug: str, member_id: int, current_user: User = Depends(org_dep.member_dep),db:Session = Depends(get_db)
):
    """Get Org  Member

    Args:
        org_slug (str): Slug
        member_id (int): Member id
        current_user (User, optional): _description_. Defaults to Depends(get_current_user): Logged in User a member of Org.

    Returns:
        _type_: resp
    """
    resp = org_service(db).get_org_member(member_id, org_slug)

    return resp


@org_router.get(
    "/{org_slug}/members/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageListOrgMemResp,
)
def get_org_members(org_slug: str, current_user: User = Depends(org_dep.member_dep),db:Session = Depends(get_db)):
    """Get All ORg Members

    Args:
        org_slug (str): slug
        current_user (User, optional): _description_. Defaults to Depends(org_dep.member_dep): Logged in Member of Org.

    Returns:
        _type_: Resp
    """
    resp = org_service(db).get_all_org_member(org_slug)

    return resp


@org_router.patch(
    "/{org_slug}/member/{member_id}/update/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgMembResp,
)
def update_org_member(
    org_slug: str,
    member_id: int,
    update_org_member: schemas.UpdateOrgMember,
    current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)
):
    """_summary_

    Args:
        org_slug (str): slug
        member_id (int): member id
        update_org_member (schemas.UpdateOrgMember): role data
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep).

    Returns:
        _type_: resp
    """
    resp = org_service(db).update_org_member(org_slug, member_id, update_org_member)

    return resp


@org_router.delete(
    "/{org_slug}/member/{member_id}/delete/",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_workspace_member(
    org_slug: str,
    member_id: int,
    current_user: User = Depends(org_dep.admin_rights_dep),db:Session = Depends(get_db)
):
    """Remove from Organization

    Args:
        org_slug (str): Slug
        member_id (int): Member id
        current_user (User, optional): _description_. Defaults to Depends(org_dep.admin_rights_dep): Logged in User with right permissions.

    Returns:
        _type_: 204
    """
    org_service(db).delete_org_member(org_slug, member_id)

    return {"status": status.HTTP_204_NO_CONTENT}


@org_router.delete(
    "/{org_slug}/member/leave/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ResponseModel,
)
def leave_workspace(org_slug: str, current_user: User = Depends(org_dep.member_dep),db:Session = Depends(get_db)):
    """Leave a Workspace

    Args:
        org_slug (str): org slug
        current_user (User, optional): _description_. Defaults to Depends(org_dep.member_dep)= Logged in User with the right permission.

    Returns:
        _type_: _description_
    """
    org_service(db).leave_org(org_slug, current_user)

    return {"status": status.HTTP_200_OK, "message": "Logged In User left Orgnizaton."}
