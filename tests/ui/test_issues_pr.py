"""TC-F07..TC-F12: issues, edytor plików, pull requesty, wyszukiwanie, wylogowanie (Selenium)."""
import base64

import pytest

from pages.base_page import BasePage
from pages.issue_pages import IssuePage, NewIssuePage
from pages.misc_pages import ComparePage, ExplorePage, FileEditorPage, PullPage
from support.api import unique

pytestmark = pytest.mark.ui


@pytest.mark.tc("TC-F07")
@pytest.mark.feature("F05", "F09")
def test_create_issue_with_label(logged_in, repo, user_api):
    full = repo["full_name"]
    user_api.create_label(*full.split("/"), "bug")
    title = unique("Błąd logowania")
    issue = NewIssuePage(logged_in, full).open().create(title, body="Kroki: 1. ...", label="bug")
    assert issue.title().startswith(title)
    assert "bug" in issue.labels()
    number = int(issue.url.rsplit("/", 1)[1])
    api_issue = user_api.get(f"/repos/{full}/issues/{number}").json()
    assert api_issue["state"] == "open"
    assert [l["name"] for l in api_issue["labels"]] == ["bug"]


@pytest.mark.tc("TC-F08")
@pytest.mark.feature("F05")
def test_issue_comment_close_and_reopen(logged_in, repo, user_api):
    full = repo["full_name"]
    number = user_api.create_issue(*full.split("/"), title="Do zamknięcia")["number"]
    page = IssuePage(logged_in).open(f"/{full}/issues/{number}")

    page.comment("Potwierdzam błąd")
    assert page.status_button_text() == "Close Issue"

    page.toggle_status(comment="Naprawione")
    assert user_api.get(f"/repos/{full}/issues/{number}").json()["state"] == "closed"
    assert page.status_button_text() == "Reopen Issue"

    page.toggle_status()
    assert user_api.get(f"/repos/{full}/issues/{number}").json()["state"] == "open"
    comments = [c["body"] for c in user_api.get(f"/repos/{full}/issues/{number}/comments").json()]
    assert comments == ["Potwierdzam błąd", "Naprawione"]


@pytest.mark.tc("TC-F09")
@pytest.mark.feature("F08", "F04")
def test_edit_file_in_web_editor(logged_in, repo, user_api):
    full = repo["full_name"]
    editor = FileEditorPage(logged_in, full, "main", "README.md").open()
    editor.replace_content("Treść zmieniona w edytorze")
    editor.commit("Aktualizacja README z UI")

    content = user_api.get(f"/repos/{full}/contents/README.md").json()["content"]
    assert base64.b64decode(content).decode().strip() == "Treść zmieniona w edytorze"
    last = user_api.get(f"/repos/{full}/commits", params={"limit": 1}).json()[0]
    assert last["commit"]["message"].strip() == "Aktualizacja README z UI"


@pytest.mark.tc("TC-F10")
@pytest.mark.feature("F06")
def test_create_and_merge_pull_request(logged_in, repo, user_api):
    full = repo["full_name"]
    owner, name = full.split("/")
    user_api.create_branch_with_change(owner, name, "feature-x", "feature.txt",
                                       base64.b64encode(b"nowa funkcja\n").decode(), "Dodaj feature.txt")
    ComparePage(logged_in, full, "main", "feature-x").open().create_pull("Dodaje feature.txt")
    pull = PullPage(logged_in)
    number = int(pull.url.rsplit("/", 1)[1])
    pull.merge()

    assert user_api.get(f"/repos/{full}/pulls/{number}").json()["merged"] is True
    assert user_api.get(f"/repos/{full}/contents/feature.txt", params={"ref": "main"}).ok


@pytest.mark.tc("TC-F11")
@pytest.mark.feature("F10")
def test_search_repository_by_name(logged_in, user_api):
    token = unique("szukaj")
    match = user_api.create_repo(f"{token}-app")
    other = user_api.create_repo()
    try:
        results = ExplorePage(logged_in).open().search(token)
        assert match["full_name"] in results
        assert other["full_name"] not in results
    finally:
        for r in (match, other):
            user_api.delete(f"/repos/{r['full_name']}")


@pytest.mark.tc("TC-F12")
@pytest.mark.feature("F02", "F07")
def test_logout_blocks_access_to_settings(logged_in):
    page = BasePage(logged_in)
    page.logout()
    assert page.logged_in_as() is None
    page.open("/user/settings")
    page.wait_url_contains("/user/login")
    assert "redirect_to=%2Fuser%2Fsettings" in page.url
