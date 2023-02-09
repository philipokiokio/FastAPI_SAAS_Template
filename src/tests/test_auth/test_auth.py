import pytest

from src.tests.conftest import TestClient, client, user_data

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
