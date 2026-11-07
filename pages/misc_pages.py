from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class FileEditorPage(BasePage):
    EDITOR = (By.CSS_SELECTOR, ".monaco-editor textarea, .cm-content, .editor-loading + div textarea")
    EDITOR_CONTAINER = (By.CSS_SELECTOR, "#editor, .monaco-editor, .cm-editor")
    COMMIT_SUMMARY = (By.CSS_SELECTOR, "input[name=commit_summary]")
    COMMIT_BUTTON = (By.ID, "commit-button")

    def __init__(self, driver, full_name: str, branch: str, path: str):
        super().__init__(driver)
        self.path = f"/{full_name}/_edit/{branch}/{path}"

    def replace_content(self, text: str) -> None:
        self.visible(self.EDITOR_CONTAINER).click()
        editor = self.find(self.EDITOR)
        editor.send_keys(Keys.CONTROL, "a")
        editor.send_keys(Keys.DELETE)
        editor.send_keys(text)

    def commit(self, summary: str) -> None:
        self.type(self.COMMIT_SUMMARY, summary)
        self.click(self.COMMIT_BUTTON)
        self.wait.until(EC.url_contains("/src/branch/"))


class ComparePage(BasePage):
    NEW_PR_BUTTON = (By.CSS_SELECTOR, ".pullrequest-form-toggle a.show-panel")
    TITLE = (By.ID, "issue_title")
    SUBMIT = (By.CSS_SELECTOR, "#new-issue button.primary[type=submit]")

    def __init__(self, driver, full_name: str, base: str, head: str):
        super().__init__(driver)
        self.path = f"/{full_name}/compare/{base}...{head}"

    def create_pull(self, title: str) -> None:
        self.click(self.NEW_PR_BUTTON)
        self.type(self.TITLE, title)
        self.click(self.SUBMIT)
        self.wait.until(EC.url_matches(r"/pulls/\d+$"))


class PullPage(BasePage):
    MERGE_FORM = (By.ID, "pull-request-merge-form")
    MERGE_BUTTON = (By.XPATH, "//*[@id='pull-request-merge-form']//button[contains(normalize-space(),'Create merge commit')]")
    MERGED_BADGE = (By.XPATH, "//*[contains(@class,'issue-state-label') or contains(@class,'label')][contains(normalize-space(),'Merged')]")

    def merge(self) -> None:
        self.visible(self.MERGE_FORM)
        # the first click expands the form, the second confirms the merge
        self.click(self.MERGE_BUTTON)
        self.wait.until(lambda d: len(d.find_elements(*self.MERGE_BUTTON)) >= 1)
        buttons = self.driver.find_elements(*self.MERGE_BUTTON)
        for b in buttons:
            if b.is_displayed() and b.get_attribute("type") == "submit":
                b.click()
                break
        self.visible(self.MERGED_BADGE)


class ExplorePage(BasePage):
    path = "/explore/repos"

    SEARCH = (By.CSS_SELECTOR, "input[name=q]")
    RESULT_LINKS = (By.CSS_SELECTOR, ".item-title a.name")

    def search(self, query: str) -> list[str]:
        """Returns full names (owner/repo) of the repositories found."""
        self.type(self.SEARCH, query)
        self.find(self.SEARCH).send_keys(Keys.ENTER)
        self.wait.until(EC.url_contains("q="))
        hrefs = [e.get_attribute("href") for e in self.driver.find_elements(*self.RESULT_LINKS)]
        paths = [h.split("://", 1)[1].split("/", 1)[1] for h in hrefs]
        return [p for p in paths if p.count("/") == 1]
