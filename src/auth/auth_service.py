from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from src.app.utils.db_utils import hash_password, verify_password
from src.app.utils.mailer_util import send_mail
from src.app.utils.token import auth_retrieve_token, auth_settings, auth_token
from src.auth import schemas
from src.auth.auth_repository import token_repo, user_repo
from src.auth.models import RefreshToken, User
from src.auth.oauth import (
    create_access_token,
    create_refresh_token,
    credential_exception,
)


class UserService:
    def __init__(self):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def register(self, user: schemas.user_create) -> User:
        user_check = self.user_repo.get_user(user.email)
        if user_check:
            raise HTTPException(
                detail="This User has an account",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user.password = hash_password(user.password)
        new_user = self.user_repo.create(user)

        token = auth_token(new_user.email)
        mail_data = {
            "first_name": new_user.first_name,
            "url": f"{auth_settings.frontend_url}/auth/verification/{token}/",
        }
        mail_title = "Verify your Account"
        template_pointer = "user/verification.html"
        await send_mail([new_user.email], mail_title, mail_data, template_pointer)

        return new_user

    def login(self, user: OAuth2PasswordRequestForm) -> schemas.LoginResponse:
        user_check = self.user_repo.get_user(user.username)
        if not user_check:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_400_BAD_REQUEST
            )

        pass_hash_check = verify_password(user_check.password, user.password)
        if not pass_hash_check:
            credential_exception()

        if user_check.is_verified is False:
            raise HTTPException(
                detail="User Account is not verified",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = create_access_token(jsonable_encoder(user_check))
        refresh_token = create_refresh_token(jsonable_encoder(user_check))

        token_check = self.token_repo.get_token(user_check.id)
        if token_check:
            token_check.token = refresh_token
            self.token_repo.update_token(token_check)
        else:
            self.token_repo.create_token(refresh_token, user_check.id)

        # access_token_ = {"access_token": access_token, "token_type": "Bearer"}
        refresh_token_ = {"token": refresh_token, "header": "Refresh-Tok"}
        login_resp = schemas.LoginResponse(
            data=user_check,
            refresh_token=refresh_token_,
        )
        resp = {
            "message": "Login Successful",
            "data": login_resp,
            "access_token": access_token,
            "token_type": "bearer",
            "status": status.HTTP_200_OK,
        }
        return resp

    def update_user(self, update_user: schemas.UserUpdate, user: User) -> User:
        update_user_dict = update_user.dict(exclude_unset=True)

        for key, value in update_user_dict.items():
            setattr(user, key, value)

        return self.user_repo.update(user)

    def delete(self, user: User) -> bool:
        return self.user_repo.delete(user)

    async def password_reset(self, user_email: str):
        user = self.user_repo.get_user(user_email)
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )

        token = auth_token(user.email)
        mail_data = {
            "first_name": user.first_name,
            "url": f"{auth_settings.frontend_url}/auth/verification/{token}/",
        }
        mail_title = "Reset your Password"
        template_pointer = "/user/verification.html"
        mail_status = await send_mail(
            [user.email], mail_title, mail_data, template_pointer
        )
        if mail_status:
            return {
                "message": "Reset Mail sent successfully",
                "status": status.HTTP_200_OK,
                "mail_status": mail_status,
            }
        else:
            return {
                "message": "Reset Mail was not sent",
                "status": status.HTTP_400_BAD_REQUEST,
                "mail_status": mail_status,
            }

    def password_reset_complete(self, token: str, password_data: schemas.PasswordData):
        data = auth_retrieve_token(token)
        if data is None:
            raise HTTPException(
                detail="Token has expired.", status_code=status.HTTP_409_CONFLICT
            )

        user = self.user_repo.get_user(data)
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )

        user.password = hash_password(password_data.password)
        self.user_repo.update(user)
        return {
            "message": "User password set successfully",
            "status": status.HTTP_200_OK,
        }

    def change_password(self, user: User, password_data: schemas.ChangePassword):
        password_check = verify_password(user.password, password_data.old_password)
        if not password_check:
            raise HTTPException(
                detail="Old Password does not corelate.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user.password = hash_password(password_data.password)
        user = self.user_repo.update(user)
        return {
            "message": "Password changed successfully",
            "data": user,
            "status": status.HTTP_200_OK,
        }

    async def resend_verification_token(self, user_email: str):
        user = self.user_repo.get_user(user_email)
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )

        token = auth_token(user.email)
        mail_data = {
            "first_name": user.first_name,
            "url": f"{auth_settings.frontend_url}/auth/verification/{token}/",
        }
        mail_title = "Verify your Account"
        template_pointer = "/user/verification.html"
        mail_status = await send_mail(
            [user.email], mail_title, mail_data, template_pointer
        )
        if mail_status:
            return {
                "message": "Account Verification Mail sent successfully",
                "status": status.HTTP_200_OK,
                "mail_status": mail_status,
            }
        else:
            return {
                "message": "Account Verification Mail was not sent",
                "status": status.HTTP_400_BAD_REQUEST,
                "mail_status": mail_status,
            }

    def account_verification_complete(self, token: str):
        data = auth_retrieve_token(token)
        if data is None:
            raise HTTPException(
                detail="Token has expired.", status_code=status.HTTP_409_CONFLICT
            )

        user = self.user_repo.get_user(data)
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        user.is_verified = True
        self.user_repo.update(user)
        return {
            "message": "User Account is verified successfully",
            "status": status.HTTP_200_OK,
        }


user_service = UserService()
