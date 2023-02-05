from fastapi import APIRouter, Depends, status
from starlette.requests import Request

from src.auth.models import User
from src.auth.oauth import get_current_user
from src.organization import schemas
from src.organization.org_service import org_service
from src.organization.pipes import org_dep

org_router = APIRouter(prefix="/api/v1/org", tags={"Organization and Org Members"})


@org_router.post(
    "/create/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MessageOrgResp,
)
def create_org(
    create_workspace: schemas.OrgCreate,
    current_user: User = Depends(org_dep.premium_ulimited_orgs),
):
    resp = org_service.create_org(current_user.id, create_workspace)

    return resp


@org_router.get(
    "s/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageListOrgResp,
)
def get_orgs(current_user: User = Depends(get_current_user)):
    resp = org_service.get_user_org(current_user.id)

    return resp


@org_router.get(
    "/{org_slug}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgResp,
)
def get_org(org_slug: str, current_user: User = Depends(org_dep.member_dep)):
    resp = org_service.get_org(org_slug)

    return resp


@org_router.patch(
    "/{org_slug}/update/",
    response_model=schemas.MessageOrgResp,
    status_code=status.HTTP_200_OK,
)
def org_update(
    org_slug: str,
    update_org: schemas.OrgUpdate,
    current_user: User = Depends(org_dep.admin_rights_dep),
):
    resp = org_service.update_org(org_slug, update_org)

    return resp


@org_router.delete(
    "/{org_slug}/delete/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def org_delete(org_slug: str, current_user: User = Depends(org_dep.admin_rights_dep)):
    org_service.delete_org(org_slug)

    return {"status": status.HTTP_204_NO_CONTENT}


@org_router.post(
    "/{org_slug}/invite-link/gen/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InviteOrgResponse,
)
def generate_org_invite_link(
    org_slug: str,
    role_data: schemas.UpdateOrgMember,
    current_user: User = Depends(org_dep.admin_rights_dep),
):
    resp = org_service.org_link_invite(org_slug, role_data.role)

    return resp


@org_router.post(
    "/{org_slug}/revoke-link/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgResp,
)
def revoke_workspace(
    org_slug: str, current_user: User = Depends(org_dep.admin_rights_dep)
):
    resp = org_service.revoke_org_link(org_slug)
    return resp


@org_router.post(
    "/join/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgMembResp,
)
def org_member_join(token: str, role_token: str, new_org_member: schemas.JoinOrg):
    resp = org_service.join_org(token, role_token, new_org_member)

    return resp


@org_router.get(
    "/{org_slug}/member/{member_id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageOrgMembResp,
)
def get_org_member(
    org_slug: str, member_id: int, current_user: User = Depends(get_current_user)
):
    resp = org_service.get_org_member(member_id, org_slug)

    return resp


@org_router.get(
    "/{org_slug}/members/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageListOrgMemResp,
)
def get_org_members(org_slug: str, current_user: User = Depends(get_current_user)):
    resp = org_service.get_all_org_member(org_slug)

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
    current_user: User = Depends(org_dep.admin_rights_dep),
):
    resp = org_service.update_org_member(org_slug, member_id, update_org_member)

    return resp


@org_router.delete(
    "/{org_slug}/member/{member_id}/delete/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workspace_member(
    org_slug: str,
    member_id: int,
    current_user: User = Depends(org_dep.admin_rights_dep),
):
    org_service.delete_org_member(org_slug, member_id)

    return {"status": status.HTTP_204_NO_CONTENT}


@org_router.delete(
    "/{org_slug}/member/leave/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ResponseModel,
)
def leave_workspace(org_slug: str, current_user: User = Depends(org_dep.member_dep)):
    org_service.leave_org(org_slug, current_user)

    return {"status": status.HTTP_200_OK, "message": "Logged In User left Orgnizaton."}
