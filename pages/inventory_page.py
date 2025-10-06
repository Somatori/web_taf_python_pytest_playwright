from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page

    # Locator-returning methods (kept private-ish)
    def _inventory_list(self):
        return self.page.locator(".inventory_list")

    def _product_add_button(self, product_id: str):
        return self.page.locator(f"[data-test='add-to-cart-{product_id}']")

    def _product_remove_button(self, product_id: str):
        return self.page.locator(f"[data-test='remove-{product_id}']")

    def _cart_button(self):
        return self.page.locator(".shopping_cart_link")

    # High-level actions (used by tests)
    def is_inventory_visible(self) -> bool:
        return self._inventory_list().is_visible()

    def add_product_to_cart(self, product_id: str):
        """Add the given product to the cart by product id (e.g. 'sauce-labs-backpack')."""
        self._product_add_button(product_id).click()

    def remove_product_from_cart(self, product_id: str):
        """Remove a product from cart (if present)."""
        self._product_remove_button(product_id).click()

    def open_cart(self):
        """Click the cart icon/link to open the cart page."""
        self._cart_button().click()

    def product_is_added(self, product_id: str) -> bool:
        """Return True if the product's remove button is visible (i.e. added)."""
        try:
            return self._product_remove_button(product_id).is_visible()
        except Exception:
            return False