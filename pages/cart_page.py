from pages.base_page import BasePage


class CartPage(BasePage):
    """Cart page with items added to cart."""

    def cart_items(self):
        # each cart item container
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

    # convenience high-level actions
    def remove_product(self, product_id: str):
        self.remove_item_button(product_id).click()

    def go_to_checkout(self):
        self.checkout_button().click()
