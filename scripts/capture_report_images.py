"""Copies representative test screenshots to docs/report/img and takes screenshots of the
pytest-html report and a GitHub Actions run (public repository - no login needed).

Usage (after `SCREENSHOTS=all pytest --html=reports/report.html ...`):
    python scripts/capture_report_images.py [URL_RUNU_ACTIONS]
"""
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from support.driver import make_driver  # noqa: E402

SHOTS = ROOT / "reports" / "screenshots"
IMG = ROOT / "docs" / "report" / "img"
SELECTED = {
    "test_login_with_wrong_password_is_rejected.png": "tc_f04_login_error.png",
    "test_register_password_length_boundary[7-chars].png": "tc_f02_password_7.png",
    "test_create_repository_with_readme.png": "tc_f05_repo_readme.png",
    "test_create_issue_with_label.png": "tc_f07_issue_label.png",
    "test_create_and_merge_pull_request.png": "tc_f10_pr_merged.png",
}


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    for src, dst in SELECTED.items():
        shutil.copy(SHOTS / src, IMG / dst)
    driver = make_driver("chrome")
    try:
        driver.get((ROOT / "reports" / "report.html").as_uri())
        time.sleep(2)
        driver.save_screenshot(str(IMG / "pytest_html_report.png"))
        if len(sys.argv) > 1:
            driver.get(sys.argv[1])
            time.sleep(4)
            driver.save_screenshot(str(IMG / "github_actions_run.png"))
    finally:
        driver.quit()
    print("\n".join(sorted(p.name for p in IMG.iterdir())))


if __name__ == "__main__":
    main()
