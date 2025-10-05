from pages.base_page import BasePage


class InventoryPage(BasePage):
    def product_add_button(self, product_id: str):
        return self.page.locator(f"[data-test='add-to-cart-{product_id}']")

    def cart_button(self):
        return self.page.locator(".shopping_cart_link")

    def inventory_list(self):
        return self.page.locator(".inventory_list")


class CartPage(BasePage):
    def checkout_button(self):
        return self.page.locator("[data-test='checkout']")


class CheckoutYourInformationPage(BasePage):
    def first_name_input(self):
        return self.page.locator("[data-test='firstName']")

    def last_name_input(self):
        return self.page.locator("[data-test='lastName']")

    def postal_code_input(self):
        return self.page.locator("[data-test='postalCode']")

    def continue_button(self):
        return self.page.locator("[data-test='continue']")


class CheckoutOverviewPage(BasePage):
    def finish_button(self):
        return self.page.locator("[data-test='finish']")


class CheckoutCompletePage(BasePage):
    def complete_header(self):
        return self.page.locator(".complete-header")
