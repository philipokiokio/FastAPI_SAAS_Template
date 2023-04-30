import pytest
from fastapi.testclient import TestClient

from src.app import main
from src.app.config import test_status
from src.app.database import Base, test_engine,TestFactory
from src.app.utils.token import gen_token
from src.auth.oauth import create_access_token, create_refresh_token
from src.app.utils.db_utils import get_db

# Test SQLAlchemy DBURL

@pytest.fixture
def session():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)






    db = TestFactory()
    try:

        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):

    # run our code beforewe  run our test
    def get_test_db():
        try:

            yield session
        finally:
            session.close()

    main.app.dependency_overrides[get_db] = get_test_db
    yield TestClient(main.app)



  

user_data = {
    "email": "test@gmail.com",
    "password": "anotherday",
    "first_name": "Philip",
    "last_name": "thebackend",
    "is_verified": False,
}


first_user_data = {
    "email": "tester@gmail.com",
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


@pytest.fixture
def first_user_login(client, first_user):
    client: TestClient = client
    res = client.post(
        "/api/v1/auth/login/",
        data={"username": first_user["email"], "password": first_user["password"]},
    )
    assert res.status_code == 200
    return res.json().get("data")


# Auth Clients for refresh and access token for the first user


@pytest.fixture
def first_user_access(first_user):
    access_token = create_access_token(first_user)
    return access_token


@pytest.fixture
def secnd_user_access(second_user):
    access_token = create_access_token(second_user)
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


@pytest.fixture
def secnd_auth_client(client, secnd_user_access):
    client: TestClient = client
    client.headers = {**client.headers, "Authorization": f"Bearer {secnd_user_access}"}
    return client


first_org = {"name": "stripe"}
second_org = {"name": "paystack"}


@pytest.fixture
def first_user_org_created(first_auth_client):
    client: TestClient = first_auth_client

    res = client.post("api/v1/org/create/", json=first_org)
    return res.json()


@pytest.fixture
def first_user_2nd_org_created(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client

    res = client.post("api/v1/org/create/", json=second_org)
    return res.json().get("data")


@pytest.fixture
def org_memb_2nd_join(first_user_2nd_org_created, client, secnd_user_access):
    client: TestClient = client

    token = gen_token(first_user_2nd_org_created["slug"])
    role_token = gen_token("Member")
    res = client.post(
        "/api/v1/org/join/",
        params={"token": token, "role_token": role_token},
        json={"email": second_user_data["email"]},
    )
    return res.json().get("data")
