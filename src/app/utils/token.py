# Token generation 3rd party generation
from itsdangerous.exc import BadSignature
from itsdangerous.url_safe import URLSafeSerializer, URLSafeTimedSerializer

# application imports
from src.app.config import auth_settings

# Creating timed and untimed data serializers
tokens = URLSafeSerializer(
    f"{auth_settings.access_secret_key}+{auth_settings.refresh_secret_key}"
)
invite_tokens = URLSafeTimedSerializer(f"{auth_settings.refresh_secret_key}")


def gen_token(data: str):
    # Token is serialized
    toks = tokens.dumps(data)

    return toks


def auth_token(data: str):
    # Timed token serializer
    return invite_tokens.dumps(data)


def retrieve_token(token: str):
    # return data from the token
    try:
        data = tokens.loads(token)
    except BadSignature:
        return None
    return data


def auth_retrieve_token(token: str):
    # return data from the token

    try:
        data = invite_tokens.loads(token, max_age=300)
    except BadSignature:
        return None
    return data
