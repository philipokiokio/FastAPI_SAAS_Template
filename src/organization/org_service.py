from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request

from src.app.config import auth_settings
from src.app.utils.schemas_utils import RoleOptions
from src.app.utils.slugger import slug_gen
from src.app.utils.token import gen_token, retrieve_token
from src.auth.auth_repository import user_repo
from src.organization import schemas
from src.organization.models import Organization, OrgMember
from src.organization.org_repository import org_member_repo, org_repo


class OrgService:
    def __init__(self):
        self.org_repo = org_repo
        self.org_member_repo = org_member_repo

    def orm_call(self, org: Organization):
        org_ = jsonable_encoder(org)
        org_["creator"] = org.creator
        org_["members"] = org.org_member
        return org_

    def member_orm_call(self, org_member: OrgMember):
        org_member_ = jsonable_encoder(org_member)
        org_member_["org"] = org_member.org
        org_member_["user"] = org_member.member
        return org_member_

    def create_org(
        self, user_id: int, org_create: schemas.OrgCreate
    ) -> schemas.MessageOrgResp:
        org_check = self.org_repo.check_org(org_create.name)
        if org_check:
            raise HTTPException(
                detail="Org exist", status_code=status.HTTP_409_CONFLICT
            )

        org_dict = org_create.dict()
        org_dict["slug"] = slug_gen()[:14]
        org_dict["created_by"] = user_id

        org = self.org_repo.create_org(org_dict)

        org_member_dict = {
            "org_id": org.id,
            "member_id": user_id,
            "role": RoleOptions.admin.value,
        }
        self.org_member_repo.create_org_member(org_member_dict)
        org = self.orm_call(org)
        resp = {
            "message": "Org Created Successfully",
            "data": org,
            "status": status.HTTP_201_CREATED,
        }

        return resp

    def get_org(self, slug: str) -> schemas.MessageOrgResp:
        org = self.org_repo.get_org(slug)
        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        org_ = self.orm_call(org)
        resp = {
            "message": "Org Returned",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def get_user_org(self, user_id: int) -> schemas.MessageListOrgResp:
        user_orgs, _ = self.org_repo.user_org_count_data(user_id)
        if not user_orgs:
            raise HTTPException(
                detail="User Does not have Orgs",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        orgs = []
        for user_org in user_orgs:
            orgs.append(self.orm_call(user_org))

        resp = {
            "message": "User Orgs retrieved successfully",
            "data": orgs,
            "status": status.HTTP_200_OK,
        }
        return resp

    def update_org(
        self, slug: str, update_org: schemas.OrgUpdate
    ) -> schemas.MessageOrgResp:
        org = self.org_repo.get_org(slug)
        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        org_update_ = update_org.dict()

        for key, value in org_update_.items():
            setattr(org, key, value)

        org = self.org_repo.update_org(org)

        org_ = self.orm_call(org)
        resp = {
            "message": "Org Updated Successfully",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def delete_org(self, slug: str):
        org = self.org_repo.get_org(slug)

        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self.org_repo.delete_org(org)

    def org_check(self, workspace):
        if not workspace:
            raise HTTPException(
                detail="Org does not exist", status_code=status.HTTP_404_NOT_FOUND
            )

    def org_link_invite(self, slug: str, role: RoleOptions):
        org = self.org_repo.get_org(slug)
        self.org_check(org)

        token = gen_token(org.slug)
        role_tok = gen_token(role)
        if org.revoke_link:
            org.revoke_link = False
            self.org_repo.update_org(org)

        name = org.name.split(" ")
        name = "-".join(name)
        invite_link = f"{auth_settings.frontend_url}{name}/invite/{token}/{role_tok}/mixer=invite/"
        resp = {
            "message": "Invite Link Created successfully",
            "data": invite_link,
            "status": status.HTTP_200_OK,
        }
        return resp

    def revoke_org_link(self, org_slug: str):
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        org.revoke_link = True
        self.org_repo.update_org(org)
        org_ = self.orm_call(org)

        resp = {
            "message": "Org revoked successfully",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def get_org_member_check(self, id: int, org_id: int):
        return self.org_member_repo.get_org_member(org_id, id)

    def org_member_check(self, org_member):
        if not org_member:
            raise HTTPException(
                detail="User is not a member of the workspace",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def org_member_check_(self, org_member):
        if org_member:
            raise HTTPException(
                detail="User is a member of the workspace",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def join_org(
        self, token: str, role_token: str, join_workspace: schemas.JoinOrg
    ) -> schemas.MessageOrgMembResp:
        token_data = retrieve_token(token)
        role_tok_data = retrieve_token(role_token)

        if not token_data:
            raise HTTPException(
                detail="Token invalid", status_code=status.HTTP_409_CONFLICT
            )
        if not role_tok_data:
            role_tok_data = RoleOptions.member

        org_check = self.org_repo.get_org(token_data)

        if not org_check:
            raise HTTPException(
                detail="Org does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        if org_check.revoke_link is True:
            raise HTTPException(
                detail="Link for Invitation has been revoked",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user_check = user_repo.get_user(join_workspace.email)
        if not user_check:
            raise HTTPException(
                detail="No account for this detail",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        org_mem_check = self.org_member_repo.get_org_member_by_user_id(
            org_check.id, user_check.id
        )
        self.org_member_check_(org_mem_check)

        org_member_data = {
            "member_id": user_check.id,
            "role": role_tok_data,
            "org_id": org_check.id,
        }

        org_member = self.org_member_repo.create_org_member(org_member_data)
        org_member_ = self.member_orm_call(org_member)

        resp = {
            "message": "User Joined Org",
            "data": org_member_,
            "status": status.HTTP_201_CREATED,
        }
        return resp

    def get_org_member(self, id: int, org_slug: str) -> schemas.MessageOrgMembResp:
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        org_member_check = self.get_org_member_check(id, org.id)
        self.org_member_check(org_member_check)
        org_member = self.member_orm_call(org_member_check)
        resp = {
            "message": "Org Member Retrieved Successfully",
            "data": org_member,
            "status": status.HTTP_200_OK,
        }

        return resp

    def get_all_org_member(self, org_slug: str) -> schemas.MessageListOrgResp:
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)

        org_member_check = self.org_member_repo.get_org_members(org.id)
        self.org_member_check(org_member_check)

        org_member_ = []
        for org_member in org_member_check:
            org_member_.append(self.member_orm_call(org_member))

        resp = {
            "message": "Org Members retrieved successfully",
            "data": org_member_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def update_org_member(
        self,
        org_slug: str,
        id: int,
        role_update: schemas.UpdateOrgMember,
    ):
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        org_member = self.org_member_repo.get_org_member(org.id, id)
        self.org_member_check(org_member)
        org_member.role = role_update.role
        org_member = self.org_member_repo.update_org_member(org_member)
        org_member_ = self.member_orm_call(org_member)
        resp = {
            "message": "Org Member Updated Successfully",
            "data": org_member_,
            "status": status.HTTP_200_OK,
        }

        return resp

    def delete_org_member(self, org_slug: str, user_id: int):
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        org_member = self.org_member_repo.get_org_member(org.id, user_id)
        self.org_member_check(org_member)
        self.org_member_repo.delete_org_member(org_member)

    def leave_org(self, org_slug: str, user_id: int):
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        org_member = self.org_member_repo.get_org_member_by_user_id(org.id, user_id)
        self.org_member_check(org_member)
        self.org_member_repo.delete_org_member(org_member)


org_service = OrgService()
