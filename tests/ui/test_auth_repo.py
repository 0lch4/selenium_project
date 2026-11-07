"""TC-F01..TC-F06: rejestracja, logowanie i zakładanie repozytoriów (Selenium)."""
import pytest

from pages.base_page import BasePage
from pages.login_page import LoginPage, RegisterPage
from pages.repo_pages import NewRepoPage, RepoPage
from support import config
from support.api import unique

pytestmark = pytest.mark.ui


@pytest.mark.tc("TC-F01")
@pytest.mark.feature("F01")
def test_register_with_valid_data(driver, admin_api):
    username = unique("reg")
    page = RegisterPage(driver).open()
    page.register(username, f"{username}@example.com", "Valid123!pass")
    try:
        page.visible(page.NAV_AVATAR)
        assert page.logged_in_as() == username
        assert admin_api.get(f"/users/{username}").status_code == 200
    finally:
        admin_api.delete_user(username)


@pytest.mark.tc("TC-F02")
@pytest.mark.feature("F01")
@pytest.mark.parametrize("length, accepted", [(7, False), (8, True)], ids=["7-znakow", "8-znakow"])
def test_register_password_length_boundary(driver, admin_api, length, accepted):
    username = unique("bva")
    password = ("Ab1!" * 3)[:length]
    page = RegisterPage(driver).open()
    page.register(username, f"{username}@example.com", password)
    try:
        if accepted:
            page.visible(page.NAV_AVATAR)
            assert page.logged_in_as() == username
        else:
            assert "cannot be less than 8 characters" in page.error_text()
            assert admin_api.get(f"/users/{username}").status_code == 404
    finally:
        admin_api.delete_user(username)


@pytest.mark.tc("TC-F03")
@pytest.mark.feature("F02")
def test_login_with_valid_credentials(driver, user):
    page = LoginPage(driver).open().login(user["username"], user["password"])
    page.visible(page.NAV_AVATAR)
    assert page.logged_in_as() == user["username"]
    assert page.url.rstrip("/") == config.BASE_URL


@pytest.mark.tc("TC-F04")
@pytest.mark.feature("F02")
def test_login_with_wrong_password_is_rejected(driver, user):
    page = LoginPage(driver).open().login(user["username"], "wrong-password")
    assert "Username or password is incorrect" in page.error_text()
    assert "/user/login" in page.url
    assert page.logged_in_as() is None


@pytest.mark.tc("TC-F05")
@pytest.mark.feature("F03", "F04")
def test_create_repository_with_readme(logged_in, user, user_api):
    name = unique("ui-repo")
    NewRepoPage(logged_in).open().create(name, description="Repo z testu Selenium")
    full = f"{user['username']}/{name}"
    try:
        repo = RepoPage(logged_in, full)
        repo.wait_url_contains(f"/{full}")
        assert "README.md" in repo.file_names()
        readme = repo.visible(repo.README).text
        assert name in readme and "Repo z testu Selenium" in readme
        api_repo = user_api.get(f"/repos/{full}").json()
        assert api_repo["description"] == "Repo z testu Selenium"
        assert api_repo["private"] is False
    finally:
        user_api.delete(f"/repos/{full}")


@pytest.mark.tc("TC-F06")
@pytest.mark.feature("F03")
def test_create_repository_with_duplicate_name(logged_in, repo, user_api):
    page = NewRepoPage(logged_in).open().create(repo["name"])
    assert "repository name is already used" in page.error_text()
    assert "/repo/create" in page.url
    repos = [r["name"] for r in user_api.get("/user/repos").json()]
    assert repos.count(repo["name"]) == 1
