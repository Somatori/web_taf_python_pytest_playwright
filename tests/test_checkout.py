from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from model.user import User

def test_add_item_and_checkout(page):
    # login
    user = User(username="standard_user", password="secret_sauce")
    login = LoginPage(page)
    login.goto()
    login.login(user.username, user.password)

    # inventory
    inv = InventoryPage(page)
    assert inv.is_displayed(), "Inventory page should be visible after login"

    # add item and go to cart
    inv.add_backpack_to_cart()
    inv.go_to_cart()

    # cart
    cart = CartPage(page)
    assert cart.has_items(), "Cart should contain at least one item"
    cart.click_checkout()

    # checkout info
    checkout = CheckoutPage(page)
    checkout.enter_customer_info("John", "Doe", "12345")
    checkout.finish_checkout()

    # verify completion
    assert checkout.is_checkout_complete(), "Checkout should complete and show confirmation"
