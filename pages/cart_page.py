from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page

    def cart_items(self):
        return self.page.locator(".cart_item")

    def cart_item_by_id(self, product_id: str):
        return self.page.locator(f".cart_item:has([data-test='remove-{product_id}'])")

    def remove_item_button(self, product_id: str):
        return self.page.locator(f"[data-test='remove-{product_id}']")

    def checkout_button(self):
        return self.page.locator("[data-test='checkout']")

    def continue_shopping_button(self):
        return self.page.locator("[data-test='continue-shopping']")

    def item_count(self) -> int:
        try:
            return self.cart_items().count()
        except Exception:
            return 0

    # high-level actions
    def remove_product(self, product_id: str):
        self.remove_item_button(product_id).click()

    def go_to_checkout(self):
        self.checkout_button().click()