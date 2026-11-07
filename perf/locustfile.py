"""Load profile for TC-NF01: typical read operations of a logged-in user."""
import os

from locust import HttpUser, between, task

USER = os.environ["PERF_USER"]
PASS = os.environ["PERF_PASS"]
REPO = os.environ["PERF_REPO"]  # owner/name


class GiteaReader(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.auth = (USER, PASS)

    @task(3)
    def repo_page(self):
        self.client.get(f"/{REPO}", name="WEB /{owner}/{repo}")

    @task(3)
    def api_repo(self):
        self.client.get(f"/api/v1/repos/{REPO}", name="API repo")

    @task(2)
    def api_issues(self):
        self.client.get(f"/api/v1/repos/{REPO}/issues?state=all&limit=20", name="API issues")

    @task(2)
    def api_search(self):
        self.client.get("/api/v1/repos/search?q=perf&limit=10", name="API search")

    @task(1)
    def explore(self):
        self.client.get("/explore/repos", name="WEB /explore/repos")
