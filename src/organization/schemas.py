from typing import List, Optional

from pydantic import EmailStr

from src.app.utils.schemas_utils import AbstractModel, ResponseModel, RoleOptions, User


class OrgCreate(AbstractModel):
    name: str


class OrgMember(AbstractModel):
    role: str
    member: User


class OrgResponse(OrgCreate):
    id: int
    slug: str
    revoke_link: Optional[bool]
    creator: User
    members: List[OrgMember] | None


class MessageOrgResp(ResponseModel):
    data: OrgResponse


class MessageListOrgResp(ResponseModel):
    data: List[OrgResponse]


class OrgUpdate(AbstractModel):
    name: Optional[str]


class UpdateRole(AbstractModel):
    role: RoleOptions


class Org(AbstractModel):
    name: str
    slug: str


class OrgMemberResponse(AbstractModel):
    id: int
    org: Org
    user: User
    role: str


class MessageOrgMembResp(ResponseModel):
    data: OrgMemberResponse


class MessageListOrgMemResp(ResponseModel):
    data: List[OrgMemberResponse]


class JoinOrg(AbstractModel):
    email: EmailStr


class UpdateOrgMember(AbstractModel):
    role: RoleOptions


class InviteOrgResponse(ResponseModel):
    data: str
