# Postęp prac

- [x] Środowisko: Gitea 28.3.0 w Dockerze, szkielet pytest/Selenium (PR #12)
- [x] Testy UI TC-F01–F06 (PR #13)
- [x] Testy UI TC-F07–F12 (PR #14)
- [x] Testy API TC-F13–F17 (PR #15)
- [x] Testy niefunkcjonalne TC-NF01–NF05, rejestr defektów (DEF-01, DEF-02)
- [x] LLM-as-a-Judge: capture 4 widoków, rubryka 8 wymiarów, judge (dry-run OK; ocena wymaga ANTHROPIC_API_KEY)
- [x] CI/CD: GitHub Actions (funkcjonalne zielone; NF z continue-on-error przez DEF-02)
- [x] Wykonanie: 38 wykonań – 36 passed, 1 failed (DEF-02), 1 xfail (DEF-01); zrzuty do raportu w docs/report/img
- [x] Dokumentacja: funkcje MoSCoW, 22 przypadki testowe wg szablonu, macierz śledzenia
- [x] LLM-as-a-Judge: cli backend (Claude Code) + .env config; real evaluation of 4 views x 3 runs – all PASS (3.75–4.0)
- [x] Report: LaTeX (sections 1–8) compiled by GitHub Actions, artifact raport-pdf
- [x] Demo: scripts/demo.ps1 (Gitea, 4 UI tests in a visible browser, judge of one view)
