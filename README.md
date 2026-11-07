# Projekt Selenium – kampania testowa Gitea

Strategia testów i kampania testowa dla aplikacji [Gitea](https://about.gitea.com/) **28.3.0**
(kurs *Testowanie i jakość oprogramowania*).

## Wymagania
- Docker + Docker Compose (np. w WSL2)
- Python 3.11+
- Google Chrome (opcjonalnie Microsoft Edge)

## Uruchomienie przedmiotu testów
```bash
bash scripts/bootstrap.sh      # Gitea na http://localhost:3000 + konto admin
```

## Uruchomienie testów
```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # Linux: .venv/bin/pip
.venv/Scripts/pytest                              # wszystkie testy
.venv/Scripts/pytest -m ui                        # tylko Selenium
HEADLESS=0 .venv/Scripts/pytest -m ui             # przeglądarka widoczna (demo)
```

## Struktura
| Katalog | Zawartość |
|---|---|
| `pages/` | Page Objects (wzorzec POM) |
| `support/` | konfiguracja, fabryka WebDrivera, klient REST API |
| `tests/` | testy automatyczne (UI, API, niefunkcjonalne) |
| `scripts/` | uruchomienie środowiska |
| `reports/` | wyniki wykonania (generowane) |
