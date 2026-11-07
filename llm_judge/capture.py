"""Etap 1 LLM-as-a-Judge: przygotowanie danych i zrzuty ekranu ocenianych widoków.

Uruchomienie:  python -m llm_judge.capture
Wynik:         llm_judge/screenshots/<widok>.png + views.json (kontekst dla sędziego)
"""
import base64
import json
from pathlib import Path

from pages.login_page import LoginPage
from support import config
from support.api import GiteaApi
from support.driver import make_driver

OUT = Path(__file__).parent / "screenshots"
DEMO_USER, DEMO_PASS, DEMO_REPO = "judge-demo", "Judge123!pass", "web-shop"


def seed(admin: GiteaApi) -> str:
    """Tworzy stały, realistyczny zestaw danych, żeby zrzuty były powtarzalne."""
    if admin.get(f"/users/{DEMO_USER}").status_code == 404:
        admin.create_user(DEMO_USER, DEMO_PASS)
    api = GiteaApi(DEMO_USER, DEMO_PASS)
    full = f"{DEMO_USER}/{DEMO_REPO}"
    if api.get(f"/repos/{full}").status_code == 404:
        api.post("/user/repos", json={"name": DEMO_REPO, "auto_init": True, "default_branch": "main",
                                      "description": "Sklep internetowy – projekt demonstracyjny"})
        for path, text in {"src/app.py": "print('shop')\n", "docs/INSTALL.md": "# Instalacja\n"}.items():
            api.post(f"/repos/{full}/contents/{path}",
                     json={"content": base64.b64encode(text.encode()).decode(), "message": f"Dodaj {path}"})
        for name, color in [("bug", "#e11d21"), ("enhancement", "#0e8a16"), ("question", "#1d76db")]:
            api.create_label(DEMO_USER, DEMO_REPO, name, color)
        labels = {l["name"]: l["id"] for l in api.get(f"/repos/{full}/labels").json()}
        issues = [("Koszyk nie zapamiętuje produktów po wylogowaniu", "bug"),
                  ("Dodać płatność BLIK", "enhancement"),
                  ("Błąd 500 przy pustym wyszukiwaniu", "bug"),
                  ("Jak skonfigurować SMTP?", "question"),
                  ("Tryb ciemny w panelu klienta", "enhancement")]
        for i, (title, label) in enumerate(issues):
            n = api.post(f"/repos/{full}/issues", json={"title": title, "labels": [labels[label]]}).json()["number"]
            if i == 3:
                api.patch(f"/repos/{full}/issues/{n}", json={"state": "closed"})
    return full


def views(full: str) -> list[dict]:
    return [
        {"id": "login", "path": "/user/login", "auth": False,
         "purpose": "Logowanie do aplikacji", "task": "Zaloguj się nazwą użytkownika i hasłem"},
        {"id": "repo_home", "path": f"/{full}", "auth": True,
         "purpose": "Strona główna repozytorium (pliki, README, nawigacja repo)",
         "task": "Odnajdź plik docs/INSTALL.md i sprawdź ostatni commit"},
        {"id": "issues_list", "path": f"/{full}/issues", "auth": True,
         "purpose": "Lista zgłoszeń z filtrami i etykietami",
         "task": "Znajdź otwarte zgłoszenia oznaczone jako bug"},
        {"id": "new_issue", "path": f"/{full}/issues/new", "auth": True,
         "purpose": "Formularz nowego zgłoszenia",
         "task": "Utwórz zgłoszenie z tytułem, opisem i etykietą"},
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    full = seed(GiteaApi(config.ADMIN_USER, config.ADMIN_PASS))
    driver = make_driver("chrome")
    try:
        meta, logged_in = [], False
        # najpierw widoki anonimowe, potem wymagające zalogowania
        for v in sorted(views(full), key=lambda v: v["auth"]):
            if v["auth"] and not logged_in:
                page = LoginPage(driver).open().login(DEMO_USER, DEMO_PASS)
                page.visible(page.NAV_AVATAR)
                logged_in = True
            driver.get(config.BASE_URL + v["path"])
            driver.execute_script("return document.fonts.ready")
            png = OUT / f"{v['id']}.png"
            driver.save_screenshot(str(png))
            meta.append({**v, "url": config.BASE_URL + v["path"], "screenshot": png.name,
                         "viewport": list(config.WINDOW_SIZE)})
            print(f"zapisano {png}")
        (OUT / "views.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
