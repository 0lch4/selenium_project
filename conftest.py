import base64
import os
from pathlib import Path

import pytest
import pytest_html

from pages.login_page import LoginPage
from support import config
from support.api import GiteaApi
from support.driver import make_driver

REPORTS = Path(__file__).parent / "reports"
SCREENSHOTS_ALL = os.getenv("SCREENSHOTS", "failed") == "all"


@pytest.fixture(scope="session")
def admin_api() -> GiteaApi:
    api = GiteaApi(config.ADMIN_USER, config.ADMIN_PASS)
    assert api.get("/version").ok, "Gitea niedostępna - uruchom scripts/bootstrap.sh"
    return api


@pytest.fixture(scope="session")
def user(admin_api):
    """Wspólny użytkownik testowy na całą sesję (usuwany na końcu)."""
    u = admin_api.create_user()
    yield u
    admin_api.delete_user(u["username"])


@pytest.fixture
def fresh_user(admin_api):
    """Osobny użytkownik dla testów modyfikujących stan konta."""
    u = admin_api.create_user()
    yield u
    admin_api.delete_user(u["username"])


@pytest.fixture(scope="session")
def user_api(user) -> GiteaApi:
    return GiteaApi(user["username"], user["password"])


@pytest.fixture
def repo(user_api):
    r = user_api.create_repo()
    yield r
    user_api.delete(f"/repos/{r['full_name']}")


@pytest.fixture
def driver(request):
    browser = getattr(request, "param", None)
    d = make_driver(browser)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture
def logged_in(driver, user):
    page = LoginPage(driver).open().login(user["username"], user["password"])
    page.visible(page.NAV_AVATAR)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Zrzut ekranu testu UI dołączany do raportu HTML.

    Domyślnie tylko przy niepowodzeniu; SCREENSHOTS=all zapisuje zrzut stanu końcowego każdego testu.
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" or not (rep.failed or SCREENSHOTS_ALL):
        return
    drv = item.funcargs.get("driver") or item.funcargs.get("logged_in")
    if drv is None:
        return
    shots = REPORTS / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    path = shots / f"{item.name}.png"
    drv.save_screenshot(str(path))
    extras = getattr(rep, "extras", [])
    extras.append(pytest_html.extras.png(base64.b64encode(path.read_bytes()).decode()))
    rep.extras = extras
