import pytest
from fastapi.testclient import TestClient

from src.app import main
from src.app.config import test_status
from src.app.database import Base, test_engine

# Test SQLAlchemy DBURL


@pytest.fixture()
def table_control():
    print("Done`")
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


@pytest.fixture()
def client(table_control):
    yield TestClient(main.app)


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
    "is_verified": True,
}


@pytest.fixture
def first_user(client):
    client: TestClient = client
    res = client.post("/api/v1/auth/register/", json=first_user_data)

    assert res.status_code == 201
    new_user = res.json()["data"]
    new_user["password"] = first_user_data["password"]
    return new_user
