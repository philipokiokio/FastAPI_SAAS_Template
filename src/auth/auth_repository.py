from pydantic import EmailStr

from src.app.utils.base_repository import BaseRepo
from src.auth.models import RefreshToken, User


class UserRepo(BaseRepo):
    def base_query(self):
        return self.db.query(User)

    def get_user(self, email: EmailStr):
        return self.base_query().filter(User.email == email).first()

    def create(self, user_create: any) -> User:
        new_user = User(**user_create.dict())
        new_user.is_verified = False
        new_user.is_premium = False
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def delete(self, user: User) -> bool:
        resp = False

        self.db.delete(user)
        self.db.commit()

        quick_check = self.base_query().filter(User.email == user.email).first()
        if not quick_check:
            resp = True
        return resp

    def update(self, user: User):
        updated_user = user
        self.db.commit()
        self.db.refresh(updated_user)
        return updated_user


class TokenRepo(BaseRepo):
    def base_query(self):
        return self.db.query(RefreshToken)

    def create_token(self, refresh_token: str, user_id: int) -> RefreshToken:
        refresh_token = RefreshToken(token=refresh_token, user_id=user_id)
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)

        return refresh_token

    def get_token(self, user_id: int):
        return self.base_query().filter(RefreshToken.user_id == user_id).first()

    def get_token_by_tok(self, token: str):
        return self.base_query().filter(RefreshToken.token == token).first()

    def update_token(self, update_token) -> RefreshToken:
        self.db.commit()
        self.db.refresh(update_token)
        return update_token


user_repo = UserRepo()
token_repo = TokenRepo()
