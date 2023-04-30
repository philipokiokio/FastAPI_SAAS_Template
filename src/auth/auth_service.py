# Framework Imports
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

# application imports
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
    def __init__(self, db):
        # Initializing Repositories
        self.db =  db
        self.user_repo = user_repo(self.db)
        self.token_repo = token_repo(self.db)

    async def register(self, user: schemas.user_create) -> User:
        # checking if user exists.
        user_check = self.user_repo.get_user(user.email)

        # raise an Exception if user exists.
        if user_check:
            raise HTTPException(
                detail="This User has an account",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # password hashing
        user.password = hash_password(user.password)
        # creating new user
        new_user = self.user_repo.create(user)
        # create new access token
        token = auth_token(new_user.email)
        # mail data inserted in to the  template
        mail_data = {
            "first_name": new_user.first_name,
            "url": f"{auth_settings.frontend_url}auth/verification/{token}/",
        }
        # mail title
        mail_title = "Verify your Account"
        template_pointer = "user/verification.html"
        # send mail
        await send_mail([new_user.email], mail_title, mail_data, template_pointer)

        return new_user

    def login(self, user: OAuth2PasswordRequestForm) -> schemas.LoginResponse:
        # check if user exists.
        user_check = self.user_repo.get_user(user.username)
        # raise exception if there is no user
        if not user_check:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_400_BAD_REQUEST
            )
        # verify that the password is correct.
        pass_hash_check = verify_password(user_check.password, user.password)
        # raise credential error
        if not pass_hash_check:
            credential_exception()
        # if user is not verified raise exception
        if user_check.is_verified is False:
            raise HTTPException(
                detail="User Account is not verified",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        # create Access and Refresh Token
        tokenizer= {"id": user_check.id, "email": user_check.email}
        access_token = create_access_token(tokenizer)
        refresh_token = create_refresh_token(tokenizer)
        # check if there is a previously existing refresh token
        token_check = self.token_repo.get_token(user_check.id)
        # if token update token column
        if token_check:
            token_check.token = refresh_token
            self.token_repo.update_token(token_check)
        else:
            # create new token data
            self.token_repo.create_token(refresh_token, user_check.id)

        # validating data via the DTO
        refresh_token_ = {"token": refresh_token, "header": "Refresh-Tok"}
        login_resp = schemas.LoginResponse(
            data=user_check,
            refresh_token=refresh_token_,
        )
        # DTO response
        resp = {
            "message": "Login Successful",
            "data": login_resp,
            "access_token": access_token,
            "token_type": "bearer",
            "status": status.HTTP_200_OK,
        }
        return resp

    def update_user(self, update_user: schemas.UserUpdate, user: User) -> User:
        # update user
        update_user_dict = update_user.dict(exclude_unset=True)

        for key, value in update_user_dict.items():
            setattr(user, key, value)

        return self.user_repo.update(user)

    def delete(self, user: User) -> bool:
        # delete user
        return self.user_repo.delete(user)

    async def password_reset(self, user_email: str):
        # check if user exist.
        user = self.user_repo.get_user(user_email)
        # raise Exception if user does not exist.
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        # create Timed Token
        token = auth_token(user.email)
        # mail data
        mail_data = {
            "first_name": user.first_name,
            "url": f"{auth_settings.frontend_url}/auth/verification/{token}/",
        }
        # mail subject
        mail_title = "Reset your Password"
        template_pointer = "/user/verification.html"
        # send mail
        mail_status = await send_mail(
            [user.email], mail_title, mail_data, template_pointer
        )
        # response based on the success or failure of sending mail
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
        # extract data from timed token
        data = auth_retrieve_token(token)
        # if data is None raise Exception
        if data is None:
            raise HTTPException(
                detail="Token has expired.", status_code=status.HTTP_409_CONFLICT
            )
        # check for user based on tokjen data

        user = self.user_repo.get_user(data)
        # raise exception if user does not exist.
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        # update newly set password in hash
        user.password = hash_password(password_data.password)
        # update user
        self.user_repo.update(user)
        return {
            "message": "User password set successfully",
            "status": status.HTTP_200_OK,
        }

    def change_password(self, user: User, password_data: schemas.ChangePassword):
        # verify oldpassword is saved in the DB
        password_check = verify_password(user.password, password_data.old_password)
        # if not True raise Exception
        if not password_check:
            raise HTTPException(
                detail="Old Password does not corelate.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # hash new password
        user.password = hash_password(password_data.password)
        # update user
        user = self.user_repo.update(user)
        # return user
        return {
            "message": "Password changed successfully",
            "data": user,
            "status": status.HTTP_200_OK,
        }

    async def resend_verification_token(self, user_email: str):
        # get user
        user = self.user_repo.get_user(user_email)
        # if not user raise Exception
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        # create timed token
        token = auth_token(user.email)
        # mail data for the template
        mail_data = {
            "first_name": user.first_name,
            "url": f"{auth_settings.frontend_url}/auth/verification/{token}/",
        }
        # mail subject
        mail_title = "Verify your Account"
        template_pointer = "/user/verification.html"
        # send email
        mail_status = await send_mail(
            [user.email], mail_title, mail_data, template_pointer
        )
        # if mail sent send this else
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
        # validate token
        data = auth_retrieve_token(token)
        # raise token Error if None
        if data is None:
            raise HTTPException(
                detail="Token has expired.", status_code=status.HTTP_409_CONFLICT
            )
        # get user based on the data
        user = self.user_repo.get_user(data)
        # if user does not exists raise Exception
        if not user:
            raise HTTPException(
                detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
            )
        # update user verification flag.
        user.is_verified = True
        self.user_repo.update(user)
        return {
            "message": "User Account is verified successfully",
            "status": status.HTTP_200_OK,
        }


# Instanting the UserService class
user_service = UserService
