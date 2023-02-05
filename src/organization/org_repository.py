from src.app.utils.base_repository import BaseRepo
from src.organization.models import Organization, OrgMember


class OrgRepo(BaseRepo):
    def base_query(self):
        return self.db.query(Organization)

    def check_org(self, name: str):
        return self.base_query().filter(Organization.name.ilike(name)).first()

    def get_org(self, slug: str):
        return self.base_query().filter(Organization.slug == slug).first()

    def get_user_orgs(self, user_id: int):
        return (
            self.base_query()
            .filter(Organization.org_member.member_id.has(id=user_id))
            .all()
        )

    def get_orgs_created_by_user(self, user_id: int):
        return self.base_query().filter(Organization.created_by == user_id).all()

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

    def create_org(self, org_create: dict):
        new_org = Organization(**org_create)
        self.db.add(new_org)
        self.db.commit()
        self.db.refresh(new_org)
        return new_org

    def update_org(self, org_update: Organization):
        self.db.commit()
        self.db.refresh(org_update)
        return org_update

    def delete_org(self, org: Organization):
        self.db.delete(org)
        self.db.commit()


class OrgMemberRepo(BaseRepo):
    def base_query(self):
        return self.db.query(OrgMember)

    def get_org_member(self, org_id: int, id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
                OrgMember.id == id,
            )
            .first()
        )

    def get_org_member_by_user_id(self, org_id: int, user_id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
                OrgMember.member_id == user_id,
            )
            .first()
        )

    def get_org_members(self, org_id: int):
        return (
            self.base_query()
            .filter(
                OrgMember.org_id == org_id,
            )
            .all()
        )

    def create_org_member(self, org_member: dict):
        new_org_member = OrgMember(**org_member)
        self.db.add(new_org_member)
        self.db.commit()
        self.db.refresh(new_org_member)
        return new_org_member

    def update_org_member(self, org_update):
        self.db.commit()
        self.db.refresh(org_update)
        return org_update

    def delete_org_member(self, org):
        self.db.delete(org)
        self.db.commit()


org_repo = OrgRepo()
org_member_repo = OrgMemberRepo()
