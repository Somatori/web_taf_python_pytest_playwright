from playwright.sync_api import Page
from configs.config import BASE_URL


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    # Locator-returning methods
    def username_input(self):
        return self.page.locator("input#user-name")

    def password_input(self):
        return self.page.locator("input#password")

    def login_button(self):
        return self.page.locator("input#login-button")

    # Page actions
    def goto(self):
        self.page.goto(BASE_URL)

    def login(self, username: str, password: str):
        self.username_input().fill(username)
        self.password_input().fill(password)
        self.login_button().click()