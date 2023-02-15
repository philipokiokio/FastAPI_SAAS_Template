import pytest

from src.app.utils.token import auth_token
from src.tests.conftest import (
    TestClient,
    client,
    first_user_data,
    second_user_data,
    user_data,
)

auth_route = "/api/v1/auth"


def test_root(client):
    client: TestClient = client
    res = client.get("/")
    assert res.json().get("message") == "Welcome to FastAPI SAAS Template"
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_registration(client):
    client: TestClient = client
    res = client.post(f"{auth_route}/register/", json=user_data)

    assert res.json().get("message") == "Registration Successful"

    assert res.json().get("data")["email"] == user_data["email"]
    assert res.status_code == 201


def test_login(client, first_user):
    client: TestClient = client
    res = client.post(
        f"{auth_route}/login/",
        data={"username": first_user["email"], "password": first_user["password"]},
    )
    assert res.status_code == 200
    assert res.json().get("message") == "Login Successful"
    data = res.json().get("data")
    assert data["data"]["email"] == first_user_data["email"]


def test_resend_verification(client, second_user):
    email_data = {"email": second_user_data["email"]}
    client: TestClient = client
    res = client.post(f"{auth_route}/resend-account-verification/", json=email_data)

    assert res.status_code == 200
    assert res.json().get("message") == "Account Verification Mail sent successfully"


def test_account_verification(client, second_user):
    client: TestClient = client
    token = auth_token(second_user_data["email"])

    res = client.post(f"{auth_route}/account-verification/{token}/")

    assert res.status_code == 200
    assert res.json().get("status") == 200
    assert res.json().get("message") == "User Account is verified successfully"


def test_fail_me(first_user, client):
    client: TestClient = client
    res = client.get(f"{auth_route}/me/")

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


def test_me(first_auth_client):
    client: TestClient = first_auth_client

    res = client.get(f"{auth_route}/me/")

    assert res.status_code == 200
    assert res.json().get("message") == "Me Data"
    assert res.json().get("data")["email"] == first_user_data["email"]


def test_update(first_auth_client):
    client: TestClient = first_auth_client

    res = client.patch(
        f"{auth_route}/update/",
        json={"first_name": "name_change", "last_name": "change_name"},
    )
    assert res.status_code == 200
    assert res.json().get("data")["first_name"] == "name_change"


def test_delete(first_auth_client):
    client: TestClient = first_auth_client

    res = client.delete(f"{auth_route}/delete/")
    assert res.status_code == 204
