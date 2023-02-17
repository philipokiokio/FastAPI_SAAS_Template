# 3rd party imports
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

# Application import
from src.app.utils.models_utils import AbstractModel
from src.auth.models import User


# Organization Table.
class Organization(AbstractModel):
    __tablename__ = "organization"
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    revoke_link = Column(Boolean, server_default=text("false"))
    creator = relationship("User")
    org_member = relationship(
        "OrgMember", back_populates="org", cascade="all, delete-orphan"
    )


# Organization Member Table.
class OrgMember(AbstractModel):
    __tablename__ = "organization_member"
    org_id = Column(
        Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
    member_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String, nullable=False)
    member = relationship("User")
    org = relationship("Organization")
