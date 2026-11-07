"""TC-NF03..TC-NF05: dostępność, bezpieczeństwo, kompatybilność (ISO/IEC 25010)."""
import json
from pathlib import Path

import pytest
import requests

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.repo_pages import NewRepoPage, RepoPage
from support import config
from support.api import unique
from support.driver import make_driver

pytestmark = pytest.mark.nonfunctional

AXE = (Path(__file__).parent / "vendor" / "axe.min.js").read_text(encoding="utf-8")
REPORTS = Path(__file__).resolve().parents[2] / "reports"


def run_axe(driver) -> list[dict]:
    driver.execute_script(AXE)
    result = driver.execute_async_script(
        "const done = arguments[arguments.length - 1];"
        "axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}})"
        "   .then(r => done(r.violations)).catch(e => done({error: e.toString()}));")
    assert not isinstance(result, dict), result
    return result


@pytest.mark.tc("TC-NF03")
@pytest.mark.feature("F01", "F02", "F04", "F05")
def test_accessibility_wcag_aa(driver, user, repo):
    pages = {"login": "/user/login", "register": "/user/sign_up"}
    report = {}
    for name, path in pages.items():
        driver.get(config.BASE_URL + path)
        report[name] = run_axe(driver)

    LoginPage(driver).open().login(user["username"], user["password"])
    for name, path in {"repo": f"/{repo['full_name']}", "issues": f"/{repo['full_name']}/issues",
                       "new_repo": "/repo/create"}.items():
        driver.get(config.BASE_URL + path)
        report[name] = run_axe(driver)

    summary = {
        page: [{"id": v["id"], "impact": v["impact"], "nodes": len(v["nodes"]), "help": v["help"]}
               for v in violations]
        for page, violations in report.items()
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "axe.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    critical = {p: [v["id"] for v in vs if v["impact"] == "critical"] for p, vs in summary.items()}
    critical = {p: ids for p, ids in critical.items() if ids}
    assert not critical, f"naruszenia krytyczne WCAG: {critical}"


@pytest.mark.tc("TC-NF04")
@pytest.mark.feature("F02", "F07")
class TestSecurity:
    def test_security_headers(self):
        r = requests.get(config.BASE_URL + "/user/login", timeout=10)
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
        assert r.headers.get("X-Frame-Options") in ("SAMEORIGIN", "DENY")

    def test_session_cookie_flags(self, user):
        s = requests.Session()
        r = s.post(config.BASE_URL + "/user/login", headers={"Origin": config.BASE_URL},
                   data={"user_name": user["username"], "password": user["password"]},
                   allow_redirects=False, timeout=10)
        cookies = [h for k, h in r.raw.headers.items() if k.lower() == "set-cookie"]
        session = [c for c in cookies if c.startswith("i_like_gitea=")]
        assert session, cookies
        assert "HttpOnly" in session[0] and "SameSite=Lax" in session[0]

    def test_cross_origin_state_change_is_rejected(self, user, user_api):
        s = requests.Session()
        s.post(config.BASE_URL + "/user/login", headers={"Origin": config.BASE_URL},
               data={"user_name": user["username"], "password": user["password"]}, timeout=10)
        name = unique("csrf")
        r = s.post(config.BASE_URL + "/repo/create",
                   headers={"Origin": "http://evil.example", "Sec-Fetch-Site": "cross-site"},
                   data={"uid": str(user["id"]), "repo_name": name, "default_branch": "main",
                         "object_format_name": "sha1"}, allow_redirects=False, timeout=10)
        assert r.status_code == 403
        assert user_api.get(f"/repos/{user['username']}/{name}").status_code == 404

    @pytest.mark.xfail(strict=True, reason="DEF-01: logowanie akceptuje żądanie cross-site (login CSRF)")
    def test_cross_origin_login_is_rejected(self, user):
        r = requests.post(config.BASE_URL + "/user/login",
                          headers={"Origin": "http://evil.example", "Sec-Fetch-Site": "cross-site"},
                          data={"user_name": user["username"], "password": user["password"]},
                          allow_redirects=False, timeout=10)
        assert r.status_code == 403

    def test_private_repo_not_leaked_to_anonymous(self, user_api):
        repo = user_api.create_repo(private=True)
        try:
            for path in (f"/{repo['full_name']}", f"/{repo['full_name']}/raw/branch/main/README.md"):
                assert requests.get(config.BASE_URL + path, timeout=10).status_code == 404
        finally:
            user_api.delete(f"/repos/{repo['full_name']}")


@pytest.mark.tc("TC-NF05")
@pytest.mark.feature("F02", "F03")
@pytest.mark.parametrize("browser", ["chrome", "edge"])
def test_cross_browser_core_flow(browser, user, user_api):
    driver = make_driver(browser)
    name = unique(f"compat-{browser}")
    try:
        page = LoginPage(driver).open().login(user["username"], user["password"])
        page.visible(page.NAV_AVATAR)
        NewRepoPage(driver).open().create(name)
        repo = RepoPage(driver, f"{user['username']}/{name}")
        assert "README.md" in repo.file_names()
        BasePage(driver).logout()
    finally:
        driver.quit()
        user_api.delete(f"/repos/{user['username']}/{name}")
