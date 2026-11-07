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
PowerShell sets the variables first: `$env:HEADLESS="0"; .venv\Scripts\pytest -m ui`.

Known defects of Gitea are reported as `xfail` (DEF-01, DEF-02 – see `docs/defects.md`), so a
complete run ends with `36 passed, 2 xfailed`.

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
No configuration is needed when Claude Code is installed and logged in (the `cli` backend).
Optionally copy `.env.example` to `.env` (git-ignored) and set one of:
- `ANTHROPIC_API_KEY=sk-ant-api...` – an Anthropic API key, uses the `api` backend,
- `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat...` – a token from `claude setup-token`, for the `cli`
  backend on a machine where Claude Code is not logged in.

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
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 -Distro Ubuntu    # Docker in another WSL distro
```
Docker reachable from Windows (Docker Desktop) is used directly; otherwise Gitea runs in Docker
inside the WSL distro (`-Distro`, default `Debian`). WSL shuts an idle distro down, which stops
Gitea – keep a `wsl -d <distro>` terminal open during the demo. The demo writes to
`reports/demo.html` and `reports/demo_judge/` and never touches the committed results.

## Submission package
```bash
git archive --format=zip -o selenium_project.zip HEAD   # source code (D2) incl. LLM judge (D3)
```
