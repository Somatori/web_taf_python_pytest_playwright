from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Inventory / Products listing page for the store."""

    def inventory_list(self):
        return self.page.locator(".inventory_list")

    def product_card(self, product_id: str):
        # returns the product card element (useful for scoping)
        return self.page.locator(f"[data-test='product-{product_id}'], .inventory_item:has([data-test='add-to-cart-{product_id}'])")

    def product_add_button(self, product_id: str):
        # button used to add a product to cart (saucedemo pattern)
        return self.page.locator(f"[data-test='add-to-cart-{product_id}']")

    def product_remove_button(self, product_id: str):
        # button used to remove a product from cart (if present)
        return self.page.locator(f"[data-test='remove-{product_id}']")

    def product_name(self, product_id: str):
        # get product name element if needed
        return self.page.locator(f".inventory_item:has([data-test='add-to-cart-{product_id}']) .inventory_item_name")

    def cart_button(self):
        # shopping cart icon / link
        return self.page.locator(".shopping_cart_link")

    # convenience high-level action (keeps tests expressive)
    def add_product_to_cart(self, product_id: str):
        self.product_add_button(product_id).click()
