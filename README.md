# Selenium project – Gitea test campaign

Test strategy and test campaign for [Gitea](https://about.gitea.com/) **28.3.0**
(course *Software testing and quality*). The test report and test design documents in
`docs/` are written in Polish for the course; code and tooling are in English.

## Requirements
- Docker + Docker Compose (e.g. in WSL2)
- Python 3.11+
- Google Chrome (optionally Microsoft Edge)

## Starting the test object
```bash
bash scripts/bootstrap.sh      # Gitea on http://localhost:3000 + admin account (admin / Admin123!pass)
```

## Running the tests
```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # Linux: .venv/bin/pip
.venv/Scripts/pytest                              # all tests
.venv/Scripts/pytest -m ui                        # Selenium only
.venv/Scripts/pytest -m "not nonfunctional"       # functional tests (as in CI)
HEADLESS=0 .venv/Scripts/pytest -m ui             # visible browser (demo)
SCREENSHOTS=all .venv/Scripts/pytest --html=reports/report.html --self-contained-html
```

## Layout
| Directory | Contents |
|---|---|
| `pages/` | Page Objects (POM pattern) |
| `support/` | configuration, WebDriver factory, REST API client |
| `tests/` | automated tests (UI, API, non-functional) |
| `perf/` | Locust load profile |
| `llm_judge/` | LLM-as-a-Judge: capture, rubric prompt, judge, results |
| `scripts/` | environment bootstrap, demo, report helpers |
| `docs/` | test design, results, defects, LaTeX report (Polish) |
| `reports/` | execution output (generated) |

## LLM-as-a-Judge (UI/UX evaluation)
```bash
.venv/Scripts/python -m llm_judge.capture          # screenshots of 4 views (1440x900) + views.json
.venv/Scripts/python -m llm_judge.judge --dry-run  # validate inputs without model calls
.venv/Scripts/python -m llm_judge.judge            # 3 runs per view, claude-opus-5-5
```
Rubric (8 dimensions, 1–5 scale): [llm_judge/prompts/judge_rubric.md](llm_judge/prompts/judge_rubric.md).
Results: `llm_judge/results/<view>.json` and `llm_judge/results/summary.md`.

### LLM-as-a-Judge – configuration
1. Copy `.env.example` to `.env` (git-ignored) and set `ANTHROPIC_API_KEY=...`.
2. Run `python -m llm_judge.judge`.

Backend selection (`--backend` or `JUDGE_BACKEND`): `auto` (default) uses `api` (Anthropic SDK)
when `ANTHROPIC_API_KEY` is set, otherwise `cli` – headless Claude Code (`claude -p`) with the
logged-in Claude Code account. `CLAUDE_BIN` points to the executable if it is not on `PATH`
(the VS Code extension binary is detected automatically). `JUDGE_MODEL` overrides the model.

## Report
`docs/report/raport.tex` is compiled by the **Report PDF** GitHub Actions workflow
(artifact `raport-pdf`); tables are generated from `docs/*.md` by `scripts/md_to_tex.py`.

## Live demo
```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1            # Gitea + 4 Selenium tests (visible browser) + judge of one view
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 -SkipJudge
```
The demo writes to `reports/demo.html` and `reports/demo_judge/` and never touches the committed results.
