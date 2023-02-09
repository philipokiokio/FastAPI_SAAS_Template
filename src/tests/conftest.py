import pytest
from fastapi.testclient import TestClient

from src.app import main
from src.app.config import data, test_status
from src.app.database import Base, test_engine


# Test SQLAlchemy DBURL
def test_settings_overide():
    return True


@pytest.fixture()
def table_control():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


@pytest.fixture()
def client(table_control):
    main.app.dependency_overrides[test_status] = test_settings_overide
    print(test_settings_overide())
    yield TestClient(main.app)


user_data = {
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
    res = client.post("/api/v1/auth/register/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()["data"]
    new_user["password"] = user_data["password"]
    return new_user
