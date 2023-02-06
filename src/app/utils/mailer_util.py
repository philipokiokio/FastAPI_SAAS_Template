from pathlib import Path
from typing import List

# 3rd party imports
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# application imports
from src.app.config import EmailStr, mail_settings

# conf configuration
conf = ConnectionConfig(
    MAIL_USERNAME=mail_settings.mail_username,
    MAIL_PASSWORD=mail_settings.mail_password,
    MAIL_FROM=mail_settings.mail_from,
    MAIL_PORT=mail_settings.mail_port,
    MAIL_SERVER=mail_settings.mail_server,
    MAIL_FROM_NAME=mail_settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / "templates/",
)


async def send_mail(
    recieptients: List[EmailStr], subject: str, body: dict, template_name: str
) -> bool:
    """Send Mail

    Args:
        recieptients (List[EmailStr]): Array of Email
        subject (str): Mail Subject
        body (dict): an Hashmap/Dict of  data
        template_name (str): the template name

    Returns:
        bool: status on success or failure.
    """
    message = MessageSchema(
        subject=subject,
        recipients=recieptients,
        template_body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)

    status = False
    try:
        await fm.send_message(message, template_name=template_name)
        status = True
    except Exception as e:
        pass
    return status
