import pytest

from src.app.utils.token import gen_token
from src.tests.conftest import TestClient, first_user_data, second_user_data

org_route = "/api/v1/org"


def test_org_creation(first_auth_client):
    client: TestClient = first_auth_client

    res = client.post(f"{org_route}/create/", json={"name": "stripe"})
    assert res.status_code == 201
    assert res.json().get("message") == "Org Created Successfully"
    assert res.json().get("data")["name"] == "stripe"


def test_org_premium(
    first_auth_client, first_user_org_created, first_user_2nd_org_created
):
    client: TestClient = first_auth_client

    res = client.post(f"{org_route}/create/", json={"name": "stripe"})

    assert res.status_code == 400
    assert (
        res.json().get("detail")
        == "Freemium Users can only create a Maximum of two Orgs"
    )


def test_orgs(first_auth_client, first_user_2nd_org_created, first_user_org_created):
    client: TestClient = first_auth_client

    res = client.get(f"{org_route}s/")

    assert res.status_code == 200
    assert type(res.json().get("data")) == list
    assert res.json().get("message") == "User Orgs retrieved successfully"


def test_get_org(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client
    slug = first_user_org_created["data"]["slug"]
    res = client.get(f"{org_route}/{slug}")

    assert res.status_code == 200
    assert res.json().get("message") == "Org Returned"
    assert res.json().get("data")["slug"] == slug
    pass


def test_update_org(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client

    slug = first_user_org_created["data"]["slug"]
    res = client.patch(f"{org_route}/{slug}/update/", json={"revoke_link": True})

    assert res.status_code == 200
    assert type(res.json().get("data")) == dict


def test_delete_org(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client

    slug = first_user_org_created["data"]["slug"]

    res = client.delete(f"{org_route}/{slug}/delete/")

    assert res.status_code == 204


def test_gen_invite_link(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client
    slug = first_user_org_created["data"]["slug"]
    res = client.post(f"{org_route}/{slug}/invite-link/gen/", json={"role": "Member"})

    assert res.status_code == 200
    assert type(res.json().get("data")) == str
    assert res.json().get("message") == "Invite Link Created successfully"


def test_revoke_invite_link(first_auth_client, first_user_org_created):
    client: TestClient = first_auth_client
    slug = first_user_org_created["data"]["slug"]
    res = client.post(f"{org_route}/{slug}/revoke-link/")

    assert res.status_code == 200
    assert res.json().get("message") == "Org revoked successfully"
    assert res.json().get("data")["slug"] == slug


@pytest.fixture
def test_org_memb_join(client, first_user_2nd_org_created, secnd_user_access):
    client: TestClient = client
    token = gen_token(first_user_2nd_org_created["slug"])
    role_token = gen_token("Member")
    res = client.post(
        f"{org_route}/join/",
        params={"token": token, "role_token": role_token},
        json={"email": second_user_data["email"]},
    )

    assert res.json().get("message") == "User Joined Org"
    assert res.status_code == 200
    assert res.json().get("data")["user"]["email"] == second_user_data["email"]
    return res.json().get("data")


def test_get_all_org_members(
    first_auth_client, first_user_2nd_org_created, org_memb_2nd_join
):
    client: TestClient = first_auth_client
    org_slug = first_user_2nd_org_created["slug"]

    res = client.get(f"{org_route}/{org_slug}/members/")

    assert res.status_code == 200

    assert res.json().get("message") == "Org Members retrieved successfully"

    for data in res.json().get("data"):
        if data["user"]["email"] == first_user_data["email"]:
            assert data["role"] == "Admin"

        elif data["user"]["email"] == second_user_data["email"]:
            assert data["role"] == "Member"


# def test_get_org_member(
#     secnd_auth_client, first_user_2nd_org_created, test_org_memb_join, secnd_user_access
# ):
#     client: TestClient = secnd_auth_client
#     slug = first_user_2nd_org_created["slug"]
#     memb_id = test_org_memb_join["id"]
#     res = client.get(f"{org_route}/{slug}/member/{memb_id}/")

#     assert res.status_code == 200
#     assert res.json().get("message") == "Org Member Retrieved Successfully"
#     assert res.json().get("data")["id"] == memb_id


def test_delete_org_memb(
    first_auth_client, first_user_2nd_org_created, test_org_memb_join, secnd_user_access
):
    client: TestClient = first_auth_client
    slug = first_user_2nd_org_created["slug"]
    memb_id = test_org_memb_join["id"]
    res = client.delete(f"{org_route}/{slug}/member/{memb_id}/delete/")

    assert res.status_code == 204


# def test_leave_org_memb(
#     first_auth_client,
#     secnd_auth_client,
#     first_user_2nd_org_created,
#     test_org_memb_join,
# ):
#     client: TestClient = secnd_auth_client
#     slug = first_user_2nd_org_created["slug"]
#     res = client.get(f"{org_route}/{slug}/member/leave/")

#     assert res.status_code == 204
