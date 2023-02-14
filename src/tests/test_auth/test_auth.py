import pytest

from src.app.utils.token import auth_token
from src.tests.conftest import TestClient, client, first_user_data, user_data

auth_route = "/api/v1/auth"


def test_root(client):
    client: TestClient = client
    res = client.get("/")
    assert res.json().get("message") == "Welcome to FastAPI SAAS Template"
    assert res.status_code == 200


def test_registration(client):
    client: TestClient = client
    res = client.post(f"{auth_route}/register/", json=user_data)

    assert res.json().get("message") == "Registration Successful"
    assert res.json().get("data")["email"] == user_data["email"]
    assert res.status_code == 201


def test_login(client):
    client: TestClient = client
    res = client.post(f"{auth_route}/login/", json=first_user_data)

    assert res.status_code == 200
    assert res.json().get("Message") == "Login Successful"
    assert res.json().get("data")["email"] == first_user_data["email"]
    pass


def test_resend_verification(client):
    email_data = {"email": user_data["email"]}
    client: TestClient = client
    res = client.post(f"{auth_route}/resend-account-verification/", json=email_data)

    assert res.status_code == 200
    assert res.json().get("message") == "Account Verification Mail sent successfully"


def test_account_verification(client):
    client: TestClient = client
    token = auth_token(user_data["email"])
    print(token)
    res = client.post(f"{auth_route}/account-verification/{token}/")
    print("No bug")
    assert res.status_code == 200
    assert res.json().get("status") == 200
    assert res.json().get("message") == "User Account is verified successfully"
