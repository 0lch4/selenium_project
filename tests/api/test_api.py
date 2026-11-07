"""TC-F13..TC-F17: functional tests at the Gitea REST API level."""
import pytest

from support.api import GiteaApi, unique

pytestmark = pytest.mark.api


@pytest.mark.tc("TC-F13")
@pytest.mark.feature("F03")
def test_repository_crud(user_api, user):
    name = unique("crud")
    full = f"{user['username']}/{name}"

    created = user_api.post("/user/repos", json={"name": name, "description": "v1"})
    assert created.status_code == 201
    assert created.json()["full_name"] == full

    assert user_api.get(f"/repos/{full}").json()["description"] == "v1"

    updated = user_api.patch(f"/repos/{full}", json={"description": "v2", "has_wiki": False})
    assert updated.status_code == 200
    assert updated.json()["description"] == "v2"
    assert updated.json()["has_wiki"] is False

    assert user_api.delete(f"/repos/{full}").status_code == 204
    assert user_api.get(f"/repos/{full}").status_code == 404


# Decision table: repo visibility x requester role -> expected HTTP status
ACCESS_TABLE = [
    ("public", "owner", 200),
    ("public", "other", 200),
    ("public", "anonymous", 200),
    ("private", "owner", 200),
    ("private", "other", 404),
    ("private", "anonymous", 404),
]


@pytest.mark.tc("TC-F14")
@pytest.mark.feature("F07")
@pytest.mark.parametrize("visibility, role, expected", ACCESS_TABLE,
                         ids=[f"{v}-{r}" for v, r, _ in ACCESS_TABLE])
def test_repository_visibility_decision_table(user_api, fresh_user, visibility, role, expected):
    repo = user_api.create_repo(private=visibility == "private")
    try:
        client = {
            "owner": user_api,
            "other": GiteaApi(fresh_user["username"], fresh_user["password"]),
            "anonymous": GiteaApi(),
        }[role]
        assert client.get(f"/repos/{repo['full_name']}").status_code == expected
    finally:
        user_api.delete(f"/repos/{repo['full_name']}")


@pytest.mark.tc("TC-F15")
@pytest.mark.feature("F07")
def test_collaborator_gains_access_to_private_repo(user_api, fresh_user):
    repo = user_api.create_repo(private=True)
    full = repo["full_name"]
    other = GiteaApi(fresh_user["username"], fresh_user["password"])
    try:
        assert other.get(f"/repos/{full}").status_code == 404

        r = user_api.put(f"/repos/{full}/collaborators/{fresh_user['username']}",
                         json={"permission": "write"})
        assert r.status_code == 204

        assert other.get(f"/repos/{full}").status_code == 200
        issue = other.post(f"/repos/{full}/issues", json={"title": "Od kolaboratora"})
        assert issue.status_code == 201

        user_api.delete(f"/repos/{full}/collaborators/{fresh_user['username']}")
        assert other.get(f"/repos/{full}").status_code == 404
    finally:
        user_api.delete(f"/repos/{full}")


@pytest.mark.tc("TC-F16")
@pytest.mark.feature("F09", "F05")
def test_milestone_progress_follows_issue_state(user_api, repo):
    full = repo["full_name"]
    ms = user_api.post(f"/repos/{full}/milestones", json={"title": "v1.0"}).json()
    numbers = [
        user_api.post(f"/repos/{full}/issues", json={"title": f"Zadanie {i}", "milestone": ms["id"]}).json()["number"]
        for i in range(2)
    ]

    state = user_api.get(f"/repos/{full}/milestones/{ms['id']}").json()
    assert (state["open_issues"], state["closed_issues"]) == (2, 0)

    user_api.patch(f"/repos/{full}/issues/{numbers[0]}", json={"state": "closed"})
    state = user_api.get(f"/repos/{full}/milestones/{ms['id']}").json()
    assert (state["open_issues"], state["closed_issues"]) == (1, 1)


@pytest.mark.tc("TC-F17")
@pytest.mark.feature("F12")
@pytest.mark.parametrize("auth, expected", [
    ("valid", 200), ("none", 401), ("invalid", 401), ("revoked", 401),
], ids=["valid", "missing", "invalid", "revoked"])
def test_api_token_authentication(user, auth, expected):
    basic = GiteaApi(user["username"], user["password"])
    token_name = unique("tok")
    r = basic.post(f"/users/{user['username']}/tokens",
                   json={"name": token_name, "scopes": ["read:user"]})
    assert r.status_code == 201
    token = r.json()["sha1"]
    try:
        if auth == "revoked":
            basic.delete(f"/users/{user['username']}/tokens/{token_name}")
        client = {
            "valid": GiteaApi(token=token),
            "none": GiteaApi(),
            "invalid": GiteaApi(token="0" * 40),
            "revoked": GiteaApi(token=token),
        }[auth]
        assert client.get("/user").status_code == expected
    finally:
        basic.delete(f"/users/{user['username']}/tokens/{token_name}")
