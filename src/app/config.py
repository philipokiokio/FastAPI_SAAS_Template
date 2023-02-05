from src.app.utils.schemas_utils import AbstractSettings, EmailStr


class DBSettings(AbstractSettings):
    name: str
    username: str
    password: str
    hostname: str
    port: int


class AuthSettings(AbstractSettings):
    access_secret_key: str
    refresh_secret_key: str
    access_time_exp: int
    refresh_time_exp: int
    algorithm: str
    frontend_url: str


class MailSettings(AbstractSettings):
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int
    mail_server: str
    mail_from_name: str


db_settings = DBSettings()
auth_settings = AuthSettings()
mail_settings = MailSettings()
