from .base_page import BasePage

class CheckoutPage(BasePage):
    # step one (information)
    FIRST_NAME = "input#first-name"
    LAST_NAME = "input#last-name"
    POSTAL_CODE = "input#postal-code"
    CONTINUE_BUTTON = 'input[data-test="continue"]'

    # overview / finish
    FINISH_BUTTON = 'button[data-test="finish"]'
    COMPLETE_HEADER = ".complete-header"

    def enter_customer_info(self, first_name: str, last_name: str, postal_code: str):
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)
        self.fill(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def finish_checkout(self):
        self.click(self.FINISH_BUTTON)

    def is_checkout_complete(self) -> bool:
        return self.is_visible(self.COMPLETE_HEADER)
