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

## LLM-as-a-Judge (ocena UI/UX)
```bash
.venv/Scripts/python -m llm_judge.capture          # zrzuty 4 widoków (1440x900) + views.json
.venv/Scripts/python -m llm_judge.judge --dry-run  # walidacja wejścia bez wywołań API
.venv/Scripts/python -m llm_judge.judge            # ocena: 3 przebiegi na widok, claude-opus-5-5
```
Wymaga klucza `ANTHROPIC_API_KEY` (PowerShell: `$env:ANTHROPIC_API_KEY="sk-ant-..."`).
Rubryka (8 wymiarów, skala 1–5): [llm_judge/prompts/judge_rubric.md](llm_judge/prompts/judge_rubric.md).
Wyniki: `llm_judge/results/<widok>.json` i `llm_judge/results/summary.md`.
