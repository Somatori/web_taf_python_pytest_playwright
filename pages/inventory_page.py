from .base_page import BasePage

class InventoryPage(BasePage):
    # selectors
    INVENTORY_LIST = ".inventory_list"
    # example specific add-to-cart button for Sauce Labs Backpack:
    ADD_BACKPACK_BTN = 'button[id="add-to-cart-sauce-labs-backpack"]'
    CART_LINK = ".shopping_cart_link"

    def is_displayed(self) -> bool:
        return self.is_visible(self.INVENTORY_LIST)

    def add_backpack_to_cart(self):
        # add a known item (stable selector)
        self.click(self.ADD_BACKPACK_BTN)

    def go_to_cart(self):
        self.click(self.CART_LINK)
