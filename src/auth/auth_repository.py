# Pydantic imports
from pydantic import EmailStr

# application import
from src.auth.models import RefreshToken, User
from sqlalchemy.orm import Session


class UserRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def base_query(self):
        # Base Query for DB calls
        return self.db.query(User)

    def get_user(self, email: EmailStr):
        # get user by email
        return self.base_query().filter(User.email.icontains(email)).first()

    def create(self, user_create: any) -> User:
        # create a new user
        new_user = User(**user_create.dict())
        new_user.is_premium = False
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def delete(self, user: User) -> bool:
        # delete user
        resp = False

        self.db.delete(user)
        self.db.commit()

        quick_check = self.base_query().filter(User.email == user.email).first()
        if not quick_check:
            resp = True
        return resp

    def update(self, user: User):
        # update user
        updated_user = user
        self.db.commit()
        self.db.refresh(updated_user)
        return updated_user


class TokenRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def base_query(self):
        # base query for refresh token
        return self.db.query(RefreshToken)

    def create_token(self, refresh_token: str, user_id: int) -> RefreshToken:
        # store refresh token
        refresh_token = RefreshToken(token=refresh_token, user_id=user_id)
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)

        return refresh_token

    def get_token(self, user_id: int):
        # filter by user_id
        return self.base_query().filter(RefreshToken.user_id == user_id).first()

    def get_token_by_tok(self, token: str):
        # filter by token
        return self.base_query().filter(RefreshToken.token == token).first()

    def update_token(self, update_token) -> RefreshToken:
        # update token
        self.db.commit()
        self.db.refresh(update_token)
        return update_token


# Instatiating the Classes.

user_repo = UserRepo
token_repo = TokenRepo
