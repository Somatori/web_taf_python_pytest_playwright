from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page

    # Locators
    def _cart_items(self):
        return self.page.locator(".cart_item")

    def _checkout_button(self):
        return self.page.locator("[data-test='checkout']")

    def _remove_item_button(self, product_id: str):
        return self.page.locator(f"[data-test='remove-{product_id}']")

    # High-level actions
    def item_count(self) -> int:
        try:
            return self._cart_items().count()
        except Exception:
            return 0

    def remove_product(self, product_id: str):
        """Remove product from the cart if present."""
        self._remove_item_button(product_id).click()

    def go_to_checkout(self):
        """Click checkout and navigate to checkout info page."""
        self._checkout_button().click()