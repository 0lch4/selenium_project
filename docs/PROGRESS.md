# Progress

- [x] Environment: Gitea 28.3.0 in Docker, pytest/Selenium skeleton (PR #12)
- [x] UI tests TC-F01–F06 (PR #13)
- [x] UI tests TC-F07–F12 (PR #14)
- [x] API tests TC-F13–F17 (PR #15)
- [x] Non-functional tests TC-NF01–NF05, defect log DEF-01, DEF-02 (PR #16)
- [x] LLM-as-a-Judge: capture of 4 views, 8-dimension rubric, judge with dry-run (PR #17)
- [x] CI/CD: GitHub Actions – functional green; non-functional with continue-on-error because of DEF-02 (PR #18)
- [x] Execution: 38 runs – 36 passed, 1 failed (DEF-02), 1 xfail (DEF-01); report screenshots in docs/report/img (PR #19)
- [x] Test design docs: MoSCoW features, 22 test cases using the template, traceability matrix (PR #20)
- [x] LLM-as-a-Judge: cli backend (Claude Code) + .env config; real evaluation of 4 views x 3 runs – all PASS, 3.75–4.0 (PR #21)
- [x] Report: LaTeX (sections 1–8) compiled by GitHub Actions, artifact `raport-pdf` (PR #22)
- [x] Demo: scripts/demo.ps1 – Gitea, 4 UI tests in a visible browser, judge of one view (PR #23)
- [x] Repository code and README translated to English (report materials in docs/ stay in Polish)
- [x] Test data in English; screenshots and LLM judge results regenerated – all PASS, 3.62–4.12
- [x] TC-NF03 marked as known defect DEF-02 (xfail strict); CI fully green
