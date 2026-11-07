from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/user/login"

    USERNAME = (By.ID, "user_name")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "form[action='/user/login'] button[type=submit]")

    def login(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self


class RegisterPage(BasePage):
    path = "/user/sign_up"

    USERNAME = (By.ID, "user_name")
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    RETYPE = (By.ID, "retype")
    SUBMIT = (By.CSS_SELECTOR, "form[action='/user/sign_up'] button[type=submit]")

    def register(self, username: str, email: str, password: str, retype: str | None = None):
        self.type(self.USERNAME, username)
        self.type(self.EMAIL, email)
        self.type(self.PASSWORD, password)
        self.type(self.RETYPE, password if retype is None else retype)
        self.click(self.SUBMIT)
        return self
