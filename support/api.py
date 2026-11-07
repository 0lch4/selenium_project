"""Cienki klient REST API Gitea używany do przygotowania danych testowych i testów API."""
import uuid

import requests

from support import config


def unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class GiteaApi:
    def __init__(self, user: str | None = None, password: str | None = None,
                 token: str | None = None, sudo: str | None = None):
        self.base = config.BASE_URL + "/api/v1"
        self.s = requests.Session()
        if token:
            self.s.headers["Authorization"] = f"token {token}"
        elif user:
            self.s.auth = (user, password)
        if sudo:
            self.s.headers["Sudo"] = sudo

    def request(self, method: str, path: str, **kw) -> requests.Response:
        return self.s.request(method, self.base + path, timeout=15, **kw)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def patch(self, path, **kw):
        return self.request("PATCH", path, **kw)

    def put(self, path, **kw):
        return self.request("PUT", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    # --- operacje administracyjne / przygotowanie danych ---

    def create_user(self, username: str | None = None, password: str = "Test123!pass") -> dict:
        username = username or unique("user")
        r = self.post("/admin/users", json={
            "username": username, "email": f"{username}@example.com",
            "password": password, "must_change_password": False,
        })
        r.raise_for_status()
        return {"username": username, "password": password, "id": r.json()["id"]}

    def delete_user(self, username: str) -> None:
        self.delete(f"/admin/users/{username}", params={"purge": "true"})

    def create_repo(self, name: str | None = None, private: bool = False,
                    auto_init: bool = True) -> dict:
        r = self.post("/user/repos", json={
            "name": name or unique("repo"), "private": private,
            "auto_init": auto_init, "default_branch": "main",
        })
        r.raise_for_status()
        return r.json()

    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> dict:
        r = self.post(f"/repos/{owner}/{repo}/issues", json={"title": title, "body": body})
        r.raise_for_status()
        return r.json()

    def create_label(self, owner: str, repo: str, name: str, color: str = "#e11d21") -> dict:
        r = self.post(f"/repos/{owner}/{repo}/labels", json={"name": name, "color": color})
        r.raise_for_status()
        return r.json()

    def create_branch_with_change(self, owner: str, repo: str, branch: str,
                                  path: str, content_b64: str, message: str) -> None:
        r = self.post(f"/repos/{owner}/{repo}/contents/{path}", json={
            "content": content_b64, "message": message,
            "branch": "main", "new_branch": branch,
        })
        r.raise_for_status()
