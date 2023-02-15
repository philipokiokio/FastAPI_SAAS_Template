# python imports
from datetime import datetime
from typing import Optional

# 3rd party
from pydantic import EmailStr

# application import
from src.app.utils.schemas_utils import AbstractModel, ResponseModel


# Email DTO (Used for token verification)
class TokenData(AbstractModel):
    email: EmailStr


# Create new user
class user_create(AbstractModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_verified: bool = False


# ORM response
class UserResponse(AbstractModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_created: datetime


# Password Data for password reset
class PasswordData(AbstractModel):
    password: str


# Password data for Change Password
class ChangePassword(PasswordData):
    old_password: str


# User Update DTO
class UserUpdate(AbstractModel):
    first_name: Optional[str]
    last_name: Optional[str]


# Req-Res Response DTO
class MessageUserResponse(ResponseModel):
    data: UserResponse


# Token DTO
class Token(AbstractModel):
    token: str


# Refresh Token DTO
class RefreshToken(Token):
    header: str


# Login ORM Response
class LoginResponse(AbstractModel):
    data: UserResponse

    refresh_token: RefreshToken


# Req-Res Login Response
class MessageLoginResponse(ResponseModel):
    data: LoginResponse
    access_token: str
    token_type: str
