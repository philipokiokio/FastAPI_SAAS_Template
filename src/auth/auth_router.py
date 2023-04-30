# framework imports
from fastapi import APIRouter, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

# application imports
from src.auth import schemas
from src.auth.auth_service import user_service
from src.auth.oauth import get_current_user, verify_refresh_token
from sqlalchemy.orm import Session
from src.app.utils.db_utils import get_db

# API Router
user_router = APIRouter(prefix="/api/v1/auth", tags=["User Authentication"])


@user_router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MessageUserResponse,
)
async def register(user_create: schemas.user_create, db:Session = Depends(get_db)):
    """Registration of User

    Args:
        user_create (schemas.user_create): {
        "first_name", "last_name","email", "password"
        }

    Returns:
        _type_: response
    """
    new_user = await user_service(db).register(user_create)
    return {
        "message": "Registration Successful",
        "data": new_user,
        "status": status.HTTP_201_CREATED,
    }


@user_router.post(
    "/login/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageLoginResponse,
)
def login(login_user: OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
    """Login

    Args:
        login_user (OAuth2PasswordRequestForm, optional):username, password

    Returns:
        _type_: user
    """
    user_login = user_service(db).login(login_user)
    return user_login


@user_router.get(
    "/me/", status_code=status.HTTP_200_OK, response_model=schemas.MessageUserResponse
)
def logged_in_user(current_user: dict = Depends(get_current_user)):
    """ME

    Args:
        current_user (dict, optional): _description_. Defaults to Depends(get_current_user): User data.

    Returns:
        _type_: User
    """
    return {"message": "Me Data", "data": current_user, "status": status.HTTP_200_OK}


@user_router.patch(
    "/update/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageUserResponse,
)
def update_user(
    update_user: schemas.UserUpdate, current_user: dict = Depends(get_current_user),db:Session = Depends(get_db)
):
    """Update User

    Args:
        update_user (schemas.UserUpdate): all user fields.
        current_user (dict, optional): _description_. Defaults to Depends(get_current_user): Logged In User.

    Returns:
        _type_: resp
    """
    update_user = user_service(db).update_user(update_user, current_user)

    return {
        "message": "User Updated Successfully",
        "data": update_user,
        "status": status.HTTP_200_OK,
    }


@user_router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(current_user: dict = Depends(get_current_user),db:Session = Depends(get_db)):
    """Delete User

    Args:
        current_user (dict, optional): _description_. Defaults to Depends(get_current_user): Logged In User

    Returns:
        _type_: 204
    """
    user_service(db).delete(current_user)
    return {"status": status.HTTP_204_NO_CONTENT}


@user_router.get("/refresh/", status_code=status.HTTP_200_OK)
def get_new_token(new_access_token: str = Depends(verify_refresh_token)):
    """New Access token

    Args:
        new_access_token (str, optional): _description_. Defaults to Depends(verify_refresh_token): Gets Access token based on refresh token.

    Returns:
        _type_: _description_
    """
    return {
        "message": "New access token created successfully",
        "token": new_access_token,
        "status": status.HTTP_200_OK,
    }


@user_router.patch(
    "/change-password/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageUserResponse,
)
def change_password(
    password_data: schemas.ChangePassword,
    current_user: dict = Depends(get_current_user),
    db:Session = Depends(get_db)    
):
    """Change Password

    Args:
        password_data (schemas.ChangePassword): {password, old_password}
        current_user (dict, optional): _description_. Defaults to Depends(get_current_user): Logged In User

    Returns:
        _type_: response
    """
    resp = user_service(db).change_password(current_user, password_data)
    return resp


@user_router.post("/password-reset/complete/{token}/", status_code=status.HTTP_200_OK)
def password_reset_complete(token: str, password_data: schemas.PasswordData,db:Session = Depends(get_db)):
    """Password Reset

    Args:
        token (str): _description_: Password reset token
        password_data (schemas.PasswordData): {password}

    Returns:
        _type_: resp
    """
    resp = user_service(db).password_reset_complete(token, password_data)
    return resp


@user_router.post("/reset-password/", status_code=status.HTTP_200_OK)
async def reset_password(password_data: schemas.TokenData,db:Session = Depends(get_db)):
    """Reset Password

    Args:
        password_data (schemas.TokenData): eemail

    Returns:
        _type_: response
    """
    resp = await user_service(db).password_reset(password_data.email)
    return resp


@user_router.post("/resend-account-verification/", status_code=status.HTTP_200_OK)
async def resend_account_verification(email_data: schemas.TokenData,db:Session = Depends(get_db)):
    """Resend Account Verification

    Args:
        email_data (schemas.TokenData): email

    Returns:
        _type_: resp
    """
    resp = await user_service(db).resend_verification_token(email_data.email)
    return resp


@user_router.post("/account-verification/{token}/", status_code=status.HTTP_200_OK)
async def account_verification(token: str,db:Session = Depends(get_db)):
    """Account Verification

    Args:
        token (str): email verification token

    Returns:
        _type_: response
    """
    resp = user_service(db).account_verification_complete(token)
    return resp
