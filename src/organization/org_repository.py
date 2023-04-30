# application imports

from src.organization.models import Organization, OrgMember
from sqlalchemy.orm import Session

class OrgRepo():
    # org base query

    def __init__(self, db:Session ) -> None:
        self.db = db
    def base_query(self):
        return self.db.query(Organization)

    # check if Org exists.
    def check_org(self, name: str):
        return self.base_query().filter(Organization.name.ilike(name)).first()

    # get org by slug
    def get_org(self, slug: str):
        return self.base_query().filter(Organization.slug == slug).first()

    # get orgs  that user is a member of.
    def get_user_orgs(self, user_id: int):
        return (
            self.base_query()
            .filter(Organization.org_member.member_id.has(id=user_id))
            .all()
        )

    # all orgs created by a user
    def get_orgs_created_by_user(self, user_id: int):
        return self.base_query().filter(Organization.created_by == user_id).all()

    # return org_count and data
    def user_org_count_data(self, user_id: int):
        user_org = (
            self.base_query()
            .filter(Organization.org_member.any(member_id=user_id))
            .all()
        )
        org_count = (
            self.base_query()
            .filter(Organization.org_member.any(member_id=user_id))
            .count()
        )
        return user_org, org_count

    # create Org
    def create_org(self, org_create: dict):
        new_org = Organization(**org_create)
        self.db.add(new_org)
        self.db.commit()
        self.db.refresh(new_org)
        return new_org

    # update Org
    def update_org(self, org_update: Organization):
        self.db.commit()
        self.db.refresh(org_update)
        return org_update

    # delete Org
    def delete_org(self, org: Organization):
        self.db.delete(org)
        self.db.commit()


class OrgMemberRepo():

    def __init__(self, db:Session) -> None:
        self.db = db
    # base query
    def base_query(self):
        return self.db.query(OrgMember)

    # get org members based on org_id and member id
    def get_org_member(self, org_id: int, id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
                OrgMember.id == id,
            )
            .first()
        )

    # get membership data based on org_id and user_id
    def get_org_member_by_user_id(self, org_id: int, user_id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
                OrgMember.member_id == user_id,
            )
            .first()
        )

    # get all org members by org_id
    def get_org_members(self, org_id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
            )
            .all()
        )

    # create org member
    def create_org_member(self, org_member: dict):
        new_org_member = OrgMember(**org_member)
        self.db.add(new_org_member)
        self.db.commit()
        self.db.refresh(new_org_member)
        return new_org_member

    # update org memeber
    def update_org_member(self, org_update):
        self.db.commit()
        self.db.refresh(org_update)
        return org_update

    # delete member
    def delete_org_member(self, org):
        self.db.delete(org)
        self.db.commit()


org_repo = OrgRepo
org_member_repo = OrgMemberRepo
