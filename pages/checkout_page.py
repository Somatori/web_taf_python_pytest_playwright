from playwright.sync_api import Page


class CheckoutYourInformationPage:
    def __init__(self, page: Page):
        self.page = page

    def _first_name(self):
        return self.page.locator("[data-test='firstName']")

    def _last_name(self):
        return self.page.locator("[data-test='lastName']")

    def _postal_code(self):
        return self.page.locator("[data-test='postalCode']")

    def _continue_button(self):
        return self.page.locator("[data-test='continue']")

    # High-level action: fill the checkout information and continue
    def fill_info_and_continue(self, first_name: str, last_name: str, postal_code: str):
        self._first_name().fill(first_name)
        self._last_name().fill(last_name)
        self._postal_code().fill(postal_code)
        self._continue_button().click()


class CheckoutOverviewPage:
    def __init__(self, page: Page):
        self.page = page

    def _finish_button(self):
        return self.page.locator("[data-test='finish']")

    def finish_checkout(self):
        """Finish the checkout flow (click Finish)."""
        self._finish_button().click()


class CheckoutCompletePage:
    def __init__(self, page: Page):
        self.page = page

    def _complete_header(self):
        return self.page.locator(".complete-header")

    def is_complete(self) -> bool:
        """Return True if the order complete header is visible."""
        try:
            return self._complete_header().is_visible()
        except Exception:
            return False