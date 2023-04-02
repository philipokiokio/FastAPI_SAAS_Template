# python imports
from typing import List, Optional, Union

# 3rd party imports
from pydantic import EmailStr

# application imports
from src.app.utils.schemas_utils import AbstractModel, ResponseModel, RoleOptions, User


# Org Create DTO
class OrgCreate(AbstractModel):
    name: str


# Org Member
class OrgMember(AbstractModel):
    role: str
    member: User


# Org Response
class OrgResponse(OrgCreate):
    id: int
    slug: str
    revoke_link: Optional[bool]
    creator: User
    members: Union[List[OrgMember], None]


# Org Response DTO
class MessageOrgResp(ResponseModel):
    data: OrgResponse


# All Org Response DTO
class MessageListOrgResp(ResponseModel):
    data: List[OrgResponse]


# Org Update
class OrgUpdate(AbstractModel):
    name: Optional[str]
    revoke_link: Optional[bool]


# Update Role
class UpdateRole(AbstractModel):
    role: RoleOptions


# ORG ORG Resp
class Org(AbstractModel):
    name: str
    slug: str


# OrgMember Response DTO
class OrgMemberResponse(AbstractModel):
    id: int
    org: Org
    user: User
    role: str


# OrgMemberResponse DTO
class MessageOrgMembResp(ResponseModel):
    data: OrgMemberResponse


# List of OrgMembersResponse DTO
class MessageListOrgMemResp(ResponseModel):
    data: List[OrgMemberResponse]


# Join Org
class JoinOrg(AbstractModel):
    email: EmailStr


# Update OrgMemberRole
class UpdateOrgMember(AbstractModel):
    role: RoleOptions


# Invite Org Resp
class InviteOrgResponse(ResponseModel):
    data: str
