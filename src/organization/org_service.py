# Fastapi imports
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# application imports
from src.app.config import auth_settings
from src.app.utils.schemas_utils import RoleOptions
from src.app.utils.slugger import slug_gen
from src.app.utils.token import gen_token, retrieve_token
from src.auth.auth_repository import user_repo
from src.organization import schemas
from src.organization.models import Organization, OrgMember
from src.organization.org_repository import org_member_repo, org_repo


class OrgService:
    def __init__(self,db):
        # intializing repository
        self.db = db
        self.org_repo = org_repo(self.db)
        self.org_member_repo = org_member_repo(self.db)

    # orm call org
    def orm_call(self, org: Organization):
        org_ = org.__dict__
        org_["creator"] = org.creator
        org_["members"] = org.org_member
        return org_

    # orm call org member
    def member_orm_call(self, org_member: OrgMember):
        org_member_ = jsonable_encoder(org_member)
        org_member_["org"] = org_member.org
        org_member_["user"] = org_member.member
        return org_member_

    def create_org(
        self, user_id: int, org_create: schemas.OrgCreate
    ) -> schemas.MessageOrgResp:
        # check org
        org_check = self.org_repo.check_org(org_create.name)
        if org_check:
            raise HTTPException(
                detail="Org exist", status_code=status.HTTP_409_CONFLICT
            )
        # data mapping
        org_dict = org_create.dict()
        org_dict["slug"] = slug_gen()[:14]
        org_dict["created_by"] = user_id

        # create org
        org = self.org_repo.create_org(org_dict)
        # org member data mapping
        org_member_dict = {
            "org_id": org.id,
            "member_id": user_id,
            "role": RoleOptions.admin.value,
        }
        # create org member
        self.org_member_repo.create_org_member(org_member_dict)
        # org orm member
        org = self.orm_call(org)
        resp = {
            "message": "Org Created Successfully",
            "data": org,
            "status": status.HTTP_201_CREATED,
        }

        return resp

    def get_org(self, slug: str) -> schemas.MessageOrgResp:
        # chek for org
        org = self.org_repo.get_org(slug)
        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # orm call
        org_ = self.orm_call(org)
        resp = {
            "message": "Org Returned",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def get_user_org(self, user_id: int) -> schemas.MessageListOrgResp:
        # all orgs a user belongs too
        user_orgs, _ = self.org_repo.user_org_count_data(user_id)
        # if not ORg raise HTTPException
        if not user_orgs:
            raise HTTPException(
                detail="User Does not have Orgs",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ORM call
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
        # check org
        org = self.org_repo.get_org(slug)
        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        # update Org
        org_update_ = update_org.dict(exclude_unset=True)
        # update org
        for key, value in org_update_.items():
            setattr(org, key, value)

        org = self.org_repo.update_org(org)
        # orm call
        org_ = self.orm_call(org)
        resp = {
            "message": "Org Updated Successfully",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    def delete_org(self, slug: str):
        # check org
        org = self.org_repo.get_org(slug)

        if not org:
            raise HTTPException(
                detail="Org does not exists",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        # delete org
        self.org_repo.delete_org(org)

    # raise HTTPException if not org
    def org_check(self, workspace):
        if not workspace:
            raise HTTPException(
                detail="Org does not exist", status_code=status.HTTP_404_NOT_FOUND
            )

    def org_link_invite(self, slug: str, role: RoleOptions):
        #  check org
        org = self.org_repo.get_org(slug)
        self.org_check(org)

        # generate tokens
        token = gen_token(org.slug)
        role_tok = gen_token(role)
        if org.revoke_link:
            org.revoke_link = False
            self.org_repo.update_org(org)

        name = org.name.split(" ")
        name = "-".join(name)
        # generate link
        invite_link = f"{auth_settings.frontend_url}{name}/invite/{token}/{role_tok}/mixer=invite/"
        resp = {
            "message": "Invite Link Created successfully",
            "data": invite_link,
            "status": status.HTTP_200_OK,
        }
        return resp

    def revoke_org_link(self, org_slug: str):
        # check for org
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        # revoke link
        org.revoke_link = True
        # org update
        self.org_repo.update_org(org)
        # orm call
        org_ = self.orm_call(org)

        resp = {
            "message": "Org revoked successfully",
            "data": org_,
            "status": status.HTTP_200_OK,
        }
        return resp

    # member org check
    def get_org_member_check(self, id: int, org_id: int):
        return self.org_member_repo.get_org_member(org_id, id)

    # raise Exception if not a member
    def org_member_check(self, org_member):
        if not org_member:
            raise HTTPException(
                detail="User is not a member of the workspace",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    # raise Exception if aleady a member
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
        # if not token_data raise Exception
        if not token_data:
            raise HTTPException(
                detail="Token invalid", status_code=status.HTTP_409_CONFLICT
            )
        # if not role_tok_data specify role to member
        if not role_tok_data:
            role_tok_data = RoleOptions.member

        # check if org exists.
        org_check = self.org_repo.get_org(token_data)

        if not org_check:
            raise HTTPException(
                detail="Org does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        # check if org link is revoked
        if org_check.revoke_link is True:
            raise HTTPException(
                detail="Link for Invitation has been revoked",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # check if invited email belongs to a user
        user_check = user_repo(self.db).get_user(join_workspace.email)
        # raise Exception if no User
        if not user_check:
            raise HTTPException(
                detail="No account for this detail",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # check if user is a member of the org
        org_mem_check = self.org_member_repo.get_org_member_by_user_id(
            org_check.id, user_check.id
        )
        self.org_member_check_(org_mem_check)
        # data mapping
        org_member_data = {
            "member_id": user_check.id,
            "role": role_tok_data,
            "org_id": org_check.id,
        }
        # create org member
        org_member = self.org_member_repo.create_org_member(org_member_data)
        # orm call
        org_member_ = self.member_orm_call(org_member)
        resp = {
            "message": "User Joined Org",
            "data": org_member_,
            "status": status.HTTP_201_CREATED,
        }

        return resp

    def get_org_member(self, id: int, org_slug: str) -> schemas.MessageOrgMembResp:
        # get Org
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        # check Org Member
        org_member_check = self.get_org_member_check(id, org.id)
        self.org_member_check(org_member_check)
        # orm call
        org_member = self.member_orm_call(org_member_check)
        resp = {
            "message": "Org Member Retrieved Successfully",
            "data": org_member,
            "status": status.HTTP_200_OK,
        }

        return resp

    def get_all_org_member(self, org_slug: str) -> schemas.MessageListOrgResp:
        # check org
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)

        # check for members
        org_member_check = self.org_member_repo.get_org_members(org.id)
        self.org_member_check(org_member_check)

        # orm call
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
        # org check
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        # member check
        org_member = self.org_member_repo.get_org_member(org.id, id)
        self.org_member_check(org_member)
        # Update role
        org_member.role = role_update.role
        # update org member insntance
        org_member = self.org_member_repo.update_org_member(org_member)
        org_member_ = self.member_orm_call(org_member)
        resp = {
            "message": "Org Member Updated Successfully",
            "data": org_member_,
            "status": status.HTTP_200_OK,
        }

        return resp

    def delete_org_member(self, org_slug: str, user_id: int):
        # check for Org
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        # checking for org memeber
        org_member = self.org_member_repo.get_org_member(org.id, user_id)
        self.org_member_check(org_member)
        # deleting the org memeber
        self.org_member_repo.delete_org_member(org_member)

    def leave_org(self, org_slug: str, user_id: int):
        # check for ORg
        org = self.org_repo.get_org(org_slug)
        self.org_check(org)
        # check for org_member innstance
        org_member = self.org_member_repo.get_org_member_by_user_id(org.id, user_id)
        self.org_member_check(org_member)
        # deleting the instance
        self.org_member_repo.delete_org_member(org_member)


org_service = OrgService
