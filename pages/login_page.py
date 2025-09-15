from .base_page import BasePage
from configs.config import BASE_URL

class LoginPage(BasePage):
    # selectors
    USERNAME_INPUT = "input#user-name"
    PASSWORD_INPUT = "input#password"
    LOGIN_BUTTON = "input#login-button"
    ERROR_MESSAGE = "h3[data-test='error']"

    def goto(self):
        super().goto(BASE_URL)

    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_text(self) -> str | None:
        return self.get_text(self.ERROR_MESSAGE)
