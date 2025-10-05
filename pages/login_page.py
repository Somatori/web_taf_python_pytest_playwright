from pages.base_page import BasePage
from configs.config import BASE_URL


class LoginPage(BasePage):
    # Locator properties (return fresh Locator on each call)
    def username_input(self):
        return self.page.locator("input#user-name")

    def password_input(self):
        return self.page.locator("input#password")

    def login_button(self):
        return self.page.locator("input#login-button")

    def goto(self):
        # use configured BASE_URL
        self.page.goto(BASE_URL)

    def login(self, username: str, password: str):
        # uses direct locators to keep things explicit & readable
        self.fill(self.username_input(), username)
        self.fill(self.password_input(), password)
        self.click(self.login_button())