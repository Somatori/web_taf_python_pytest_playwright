from playwright.sync_api import Page


class CheckoutYourInformationPage:
    def __init__(self, page: Page):
        self.page = page

    def first_name_input(self):
        return self.page.locator("[data-test='firstName']")

    def last_name_input(self):
        return self.page.locator("[data-test='lastName']")

    def postal_code_input(self):
        return self.page.locator("[data-test='postalCode']")

    def continue_button(self):
        return self.page.locator("[data-test='continue']")


class CheckoutOverviewPage:
    def __init__(self, page: Page):
        self.page = page

    def finish_button(self):
        return self.page.locator("[data-test='finish']")


class CheckoutCompletePage:
    def __init__(self, page: Page):
        self.page = page

    def complete_header(self):
        return self.page.locator(".complete-header")