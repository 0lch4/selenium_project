"""Environment smoke tests - confirm the test object is ready before the campaign."""
import pytest

from pages.base_page import BasePage


def test_api_version(admin_api):
    assert admin_api.get("/version").json()["version"].startswith("28.")


@pytest.mark.ui
def test_login_fixture(logged_in, user):
    assert BasePage(logged_in).logged_in_as() == user["username"]
