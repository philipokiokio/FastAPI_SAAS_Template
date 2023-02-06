# 3rd party imports
from sqlalchemy import Boolean, Column, ForeignKey, String, text
from sqlalchemy.orm import relationship

# application imports
from src.app.utils.models_utils import AbstractModel


class User(AbstractModel):
    # User Table
    __tablename__ = "users"
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default=text("false"))
    is_premium = Column(Boolean, nullable=False, server_default=text("false"))


class RefreshToken(AbstractModel):
    # Refresh Token Table
    __tablename__ = "user_refresh_token"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False)
    user = relationship("User", passive_deletes=True)
