from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from support import config

Locator = tuple[str, str]


class BasePage:
    path = "/"

    FLASH_ERROR = (By.CSS_SELECTOR, ".flash-error, .ui.negative.message")
    FLASH_SUCCESS = (By.CSS_SELECTOR, ".flash-success, .ui.positive.message")
    NAV_AVATAR = (By.CSS_SELECTOR, ".navbar-avatar")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".user-menu a[href='/user/logout']")
    SIGN_IN_LINK = (By.CSS_SELECTOR, "#navbar a[href^='/user/login']")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        # Gitea przeładowuje stronę po akcjach fetch - elementy mogą chwilowo stać się nieaktualne
        self.wait = WebDriverWait(driver, config.DEFAULT_TIMEOUT,
                                  ignored_exceptions=(StaleElementReferenceException,))

    def open(self, path: str | None = None):
        self.driver.get(config.BASE_URL + (path or self.path))
        return self

    def find(self, loc: Locator) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(loc))

    def visible(self, loc: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(loc))

    def click(self, loc: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(loc)).click()

    def type(self, loc: Locator, text: str) -> None:
        el = self.visible(loc)
        el.clear()
        el.send_keys(text)

    def is_present(self, loc: Locator) -> bool:
        return bool(self.driver.find_elements(*loc))

    def error_text(self) -> str:
        return self.visible(self.FLASH_ERROR).text

    def logged_in_as(self) -> str | None:
        avatars = self.driver.find_elements(By.CSS_SELECTOR, ".navbar-avatar img")
        return avatars[0].get_attribute("title") if avatars else None

    def logout(self) -> None:
        self.click(self.NAV_AVATAR)
        self.click(self.LOGOUT_LINK)
        self.visible(self.SIGN_IN_LINK)

    def wait_url_contains(self, fragment: str) -> None:
        self.wait.until(EC.url_contains(fragment))

    @property
    def url(self) -> str:
        return self.driver.current_url
