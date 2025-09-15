from .base_page import BasePage

class CartPage(BasePage):
    CART_ITEM = ".cart_item"
    CHECKOUT_BUTTON = 'button[data-test="checkout"]'

    def has_items(self) -> bool:
        try:
            return self.is_visible(self.CART_ITEM)
        except Exception:
            return False

    def click_checkout(self):
        self.click(self.CHECKOUT_BUTTON)
