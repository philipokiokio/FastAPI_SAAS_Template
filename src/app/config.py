from typing import Optional

from src.app.utils.schemas_utils import AbstractSettings, BaseModel, EmailStr


class DBSettings(AbstractSettings):
    """Database Settings

    Args:
        AbstractSettings (_type_): inherits Core settings.
    """

    name: str
    username: str
    password: str
    hostname: str
    port: int


class AuthSettings(AbstractSettings):
    """Authentication Settings

    Args:
        AbstractSettings (_type_): inherits Core settings.
    """

    access_secret_key: str
    refresh_secret_key: str
    access_time_exp: int
    refresh_time_exp: int
    algorithm: str
    frontend_url: str


class MailSettings(AbstractSettings):
    """Mail Settings

    Args:
        AbstractSettings (_type_): inherits Core settings.
    """

    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int
    mail_server: str
    mail_from_name: str


class TestSettings(AbstractSettings):
    should_test: Optional[bool]


db_settings = DBSettings()
auth_settings = AuthSettings()
mail_settings = MailSettings()
test_status = TestSettings()
