from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class NewRepoPage(BasePage):
    path = "/repo/create"

    NAME = (By.ID, "repo_name")
    DESCRIPTION = (By.ID, "description")
    PRIVATE = (By.CSS_SELECTOR, "input[name=private]")
    AUTO_INIT = (By.CSS_SELECTOR, "input[name=auto_init]")
    SUBMIT = (By.CSS_SELECTOR, "form.new-repo-form button.primary[type=submit]")

    def _set_checkbox(self, loc, value: bool) -> None:
        box = self.find(loc)
        if box.is_selected() != value:
            # Fomantic UI checkboxes are hidden - click the parent label
            box.find_element(By.XPATH, "..").click()

    def create(self, name: str, description: str = "", private: bool = False,
               init_readme: bool = True):
        self.type(self.NAME, name)
        if description:
            self.type(self.DESCRIPTION, description)
        self._set_checkbox(self.PRIVATE, private)
        self._set_checkbox(self.AUTO_INIT, init_readme)
        self.click(self.SUBMIT)
        return self


class RepoPage(BasePage):
    FILE_ENTRIES = (By.CSS_SELECTOR, "#repo-files-table .repo-file-cell.name a")
    README = (By.CSS_SELECTOR, "#readme")
    PRIVATE_BADGE = (By.CSS_SELECTOR, ".repo-header .ui.label, .repo-title + .ui.label")

    def __init__(self, driver, full_name: str):
        super().__init__(driver)
        self.path = f"/{full_name}"

    def file_names(self) -> list[str]:
        self.visible(self.FILE_ENTRIES)
        return [e.text.strip() for e in self.driver.find_elements(*self.FILE_ENTRIES)]
