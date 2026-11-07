from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class NewIssuePage(BasePage):
    TITLE = (By.ID, "issue_title")
    BODY = (By.CSS_SELECTOR, "#new-issue textarea[name=content]")
    LABELS_DROPDOWN = (By.XPATH, "//input[@name='label_ids']/following-sibling::div[contains(@class,'dropdown')]")
    SUBMIT = (By.CSS_SELECTOR, "#new-issue button.primary[type=submit]")

    def __init__(self, driver, full_name: str):
        super().__init__(driver)
        self.path = f"/{full_name}/issues/new"

    def select_label(self, name: str) -> None:
        self.click(self.LABELS_DROPDOWN)
        self.click((By.XPATH, f"//input[@name='label_ids']/following-sibling::div"
                              f"//div[contains(@class,'menu')]//*[contains(@class,'item')][.//*[normalize-space()='{name}']]"))
        # closing the dropdown commits the label selection
        self.click(self.TITLE)

    def create(self, title: str, body: str = "", label: str | None = None):
        self.type(self.TITLE, title)
        if body:
            self.type(self.BODY, body)
        if label:
            self.select_label(label)
        self.click(self.SUBMIT)
        self.wait.until(EC.url_matches(r"/issues/\d+$"))
        return IssuePage(self.driver)


class IssuePage(BasePage):
    TITLE = (By.CSS_SELECTOR, "#issue-title-display, .issue-title h1")
    LABELS = (By.CSS_SELECTOR, ".issue-content-right .labels-list .item, .issue-content-right .labels-list a")
    COMMENT_BOX = (By.CSS_SELECTOR, "#comment-form textarea[name=content]")
    COMMENT_BUTTON = (By.ID, "comment-button")
    STATUS_BUTTON = (By.ID, "status-button")
    COMMENTS = (By.CSS_SELECTOR, ".timeline-item.comment .render-content")

    def title(self) -> str:
        return self.visible(self.TITLE).text.strip()

    def labels(self) -> list[str]:
        return [e.text.strip() for e in self.driver.find_elements(*self.LABELS) if e.text.strip()]

    def status_button_text(self) -> str:
        return self.visible(self.STATUS_BUTTON).text.strip()

    def comment(self, text: str) -> None:
        self.type(self.COMMENT_BOX, text)
        self.click(self.COMMENT_BUTTON)
        self.wait.until(lambda d: any(text in c.text for c in d.find_elements(*self.COMMENTS)))

    def toggle_status(self, comment: str = "") -> None:
        if comment:
            self.type(self.COMMENT_BOX, comment)
        button = self.wait.until(EC.element_to_be_clickable(self.STATUS_BUTTON))
        button.click()
        # the form is submitted via fetch, then the page reloads
        self.wait.until(EC.staleness_of(button))
        self.visible(self.STATUS_BUTTON)
