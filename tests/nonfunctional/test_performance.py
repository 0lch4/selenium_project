"""TC-NF01, TC-NF02: wydajność (ISO/IEC 25010 - Performance efficiency / time behaviour)."""
import csv
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from support import config

pytestmark = pytest.mark.nonfunctional

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

# Parametry profilu obciążenia i kryteria akceptacji
USERS, SPAWN_RATE, DURATION = 20, 5, os.getenv("PERF_DURATION", "30s")
P95_LIMIT_MS, MIN_RPS, MAX_ERROR_RATE = 500, 10, 0.0
PAGE_LOAD_LIMIT_MS = 2000


@pytest.mark.tc("TC-NF01")
@pytest.mark.feature("F04", "F05", "F10")
def test_api_response_time_under_load(user, user_api):
    repo = user_api.create_repo("perf-target")
    for i in range(20):
        user_api.create_issue(*repo["full_name"].split("/"), title=f"perf issue {i}")
    out = REPORTS / "perf"
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PERF_USER": user["username"], "PERF_PASS": user["password"],
           "PERF_REPO": repo["full_name"]}
    try:
        subprocess.run(
            [sys.executable, "-m", "locust", "-f", str(ROOT / "perf" / "locustfile.py"),
             "--headless", "-u", str(USERS), "-r", str(SPAWN_RATE), "-t", DURATION,
             "--host", config.BASE_URL, "--csv", str(out / "locust"), "--only-summary"],
            env=env, check=False, capture_output=True, timeout=300,
        )
        with open(out / "locust_stats.csv", newline="") as f:
            rows = {r["Name"]: r for r in csv.DictReader(f)}
    finally:
        user_api.delete(f"/repos/{repo['full_name']}")

    total = rows["Aggregated"]
    requests_n = int(total["Request Count"])
    error_rate = int(total["Failure Count"]) / max(requests_n, 1)
    summary = {
        name: {"p50": float(r["50%"]), "p95": float(r["95%"]), "rps": float(r["Requests/s"])}
        for name, r in rows.items()
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))

    assert requests_n > 0
    assert error_rate <= MAX_ERROR_RATE, f"błędy: {error_rate:.1%}"
    assert float(total["Requests/s"]) >= MIN_RPS
    slow = {n: s["p95"] for n, s in summary.items() if s["p95"] > P95_LIMIT_MS}
    assert not slow, f"p95 > {P95_LIMIT_MS} ms: {slow}"


PAGES = ["/", "/explore/repos", "/{repo}", "/{repo}/issues", "/user/settings"]


@pytest.mark.tc("TC-NF02")
@pytest.mark.feature("F02", "F04", "F05", "F10")
def test_page_load_time(driver, user, repo):
    LoginPage(driver).open().login(user["username"], user["password"])
    results = {}
    for path in PAGES:
        url = config.BASE_URL + path.format(repo=repo["full_name"])
        samples = []
        for _ in range(3):
            driver.get(url)
            nav = driver.execute_script(
                "const n = performance.getEntriesByType('navigation')[0];"
                "return {load: n.loadEventEnd - n.startTime, ttfb: n.responseStart - n.startTime};")
            samples.append(nav["load"])
        results[path] = statistics.median(samples)

    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "page_load.json").write_text(json.dumps(results, indent=2))
    slow = {p: t for p, t in results.items() if t > PAGE_LOAD_LIMIT_MS}
    assert not slow, f"strony wolniejsze niż {PAGE_LOAD_LIMIT_MS} ms: {slow}"
