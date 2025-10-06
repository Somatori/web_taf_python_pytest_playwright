from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page

    def inventory_list(self):
        return self.page.locator(".inventory_list")

    def product_card(self, product_id: str):
        return self.page.locator(f".inventory_item:has([data-test='add-to-cart-{product_id}'])")

    def product_add_button(self, product_id: str):
        return self.page.locator(f"[data-test='add-to-cart-{product_id}']")

    def product_remove_button(self, product_id: str):
        return self.page.locator(f"[data-test='remove-{product_id}']")

    def product_name(self, product_id: str):
        return self.page.locator(f".inventory_item:has([data-test='add-to-cart-{product_id}']) .inventory_item_name")

    def cart_button(self):
        return self.page.locator(".shopping_cart_link")

    # convenience action using locator directly
    def add_product_to_cart(self, product_id: str):
        self.product_add_button(product_id).click()