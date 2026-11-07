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
Rubryka (8 wymiarów, skala 1–5): [llm_judge/prompts/judge_rubric.md](llm_judge/prompts/judge_rubric.md).
Wyniki: `llm_judge/results/<widok>.json` i `llm_judge/results/summary.md`.

### LLM-as-a-Judge – configuration
1. Copy `.env.example` to `.env` (git-ignored) and set `ANTHROPIC_API_KEY=...`.
2. Run `python -m llm_judge.judge`.

Backend selection (`--backend` or `JUDGE_BACKEND`): `auto` (default) uses `api` (Anthropic SDK)
when `ANTHROPIC_API_KEY` is set, otherwise `cli` – headless Claude Code (`claude -p`) with the
logged-in Claude Code account. `CLAUDE_BIN` points to the executable if it is not on `PATH`
(the VS Code extension binary is detected automatically). `JUDGE_MODEL` overrides the model.

## Live demo
```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1            # Gitea + 4 Selenium tests (visible browser) + judge of one view
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 -SkipJudge
```
The demo writes to `reports/demo.html` and `reports/demo_judge/` and never touches the committed results.
