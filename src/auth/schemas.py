from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from src.app.utils.schemas_utils import AbstractModel, ResponseModel


class TokenData(AbstractModel):
    email: EmailStr


class user_create(AbstractModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(AbstractModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_created: datetime

    class Config:
        orm_mode = True


class PasswordData(AbstractModel):
    password: str


class ChangePassword(PasswordData):
    old_password: str


class UserUpdate(AbstractModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]


class MessageUserResponse(ResponseModel):
    data: UserResponse


class Token(AbstractModel):
    token: str


class RefreshToken(Token):
    header: str


class LoginResponse(AbstractModel):
    data: UserResponse

    refresh_token: RefreshToken

    class Config:
        orm_mode = True


class MessageLoginResponse(ResponseModel):
    data: LoginResponse
    access_token: str
    token_type: str
