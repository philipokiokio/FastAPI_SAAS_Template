import pytest
from fastapi.testclient import TestClient

from src.app import main
from src.app.config import test_status
from src.app.database import Base, TestSessionLocal, test_engine
from src.auth.oauth import create_access_token, create_refresh_token

# Test SQLAlchemy DBURL


@pytest.fixture
def table_control():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


@pytest.fixture
def client(table_control):
    try:
        yield TestClient(main.app)
    finally:
        TestSessionLocal.close()


user_data = {
    "email": "test@gmail.com",
    "password": "anotherday",
    "first_name": "Philip",
    "last_name": "thebackend",
    "is_verified": False,
}


first_user_data = {
    "email": "test@gmail.com",
    "password": "anotherday",
    "first_name": "Philip",
    "last_name": "thebackend",
    "is_verified": True,
}

second_user_data = {
    "email": "test@mail.com",
    "password": "anotherday",
    "first_name": "Philip",
    "last_name": "thebackend",
    "is_verified": False,
}


@pytest.fixture
def first_user(client):
    client: TestClient = client
    res = client.post("/api/v1/auth/register/", json=first_user_data)

    assert res.status_code == 201
    new_user = res.json()["data"]
    new_user["password"] = first_user_data["password"]
    return new_user


@pytest.fixture
def second_user(client):
    client: TestClient = client
    res = client.post("/api/v1/auth/register/", json=second_user_data)

    assert res.status_code == 201
    new_user = res.json()["data"]
    new_user["password"] = second_user_data["password"]
    return new_user


# Auth Clients for refresh and access token for the first user


@pytest.fixture
def first_user_access(first_user):
    access_token = create_access_token(first_user)
    return access_token


@pytest.fixture
def first_user_refresh(first_user):
    data = {"email": first_user["email"]}
    refresh_token = create_refresh_token(data)
    return refresh_token


@pytest.fixture
def first_auth_client(client, first_user_access):
    client: TestClient = client
    client.headers = {**client.headers, "Authorization": f"Bearer {first_user_access}"}
    return client
