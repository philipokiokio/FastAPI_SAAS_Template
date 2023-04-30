# python import
from datetime import datetime, timedelta

# framework imports
from fastapi import Depends, Header, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# JWT imports
from jose import JWTError, jwt

# Apoplication imports
from src.app.config import auth_settings
from src.app.utils.db_utils import get_db
from src.auth.auth_repository import token_repo, user_repo
from src.auth.schemas import TokenData

# OAUTH Login Endpoint
oauth_schemes = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")


# AUTH SECRETS AND TIME LIMITS
access_secret_key = auth_settings.access_secret_key
refresh_secret_key = auth_settings.refresh_secret_key
access_time_exp = auth_settings.access_time_exp
refresh_time_exp = auth_settings.refresh_time_exp
Algorithm = auth_settings.algorithm


def create_access_token(data: dict) -> str:
    # Create Access Token
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=access_time_exp)
    to_encode["exp"] = expire
    encode_jwt = jwt.encode(to_encode, access_secret_key, algorithm=Algorithm)
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    # Create Refresh Token
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=refresh_time_exp)
    to_encode["exp"] = expire
    refresh_encode_jwt = jwt.encode(to_encode, refresh_secret_key, algorithm=Algorithm)
    return refresh_encode_jwt


def credential_exception():
    # Throw Auth Exception
    raise HTTPException(
        detail="Could not validate credentials",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )


def refresh_exception():
    # Throw Refresh Exception

    raise HTTPException(
        detail="Could not validate refresh credential",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"Refresh-Tok": "token"},
    )


def verify_refresh_token(refresh_tok: str = Header(),db:Session = Depends(get_db)) -> str:
    # Verify Refresh Token
    try:
        decoded_data = jwt.decode(refresh_tok, refresh_secret_key, algorithms=Algorithm)
        email = decoded_data.get("email")
        if not email:
            raise refresh_exception()
        token_data = TokenData(email=email)
    except JWTError:
        raise refresh_exception()

    refresh_token_check = token_repo(db).get_token_by_tok(refresh_tok)

    if not refresh_token_check:
        refresh_exception()

    if refresh_token_check.user.email != token_data.email:
        refresh_exception()

    return create_access_token(decoded_data)


def get_current_user(token: str = Depends(oauth_schemes), db:Session = Depends(get_db)):
    # Verify Access token and return User
    try:
        decode_data = jwt.decode(token, access_secret_key, algorithms=Algorithm)
        email = decode_data.get("email")
        if email is None:
            credential_exception()

        token_data = TokenData(email=email)
    except JWTError:
        credential_exception()

    user_check = user_repo(db).get_user(token_data.email)

    if not user_check:
        credential_exception()

    return user_check
