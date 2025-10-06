from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutYourInformationPage, CheckoutOverviewPage, CheckoutCompletePage


def test_add_item_and_checkout(page, credentials):
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    inventory = InventoryPage(page)
    inventory.add_product_to_cart("sauce-labs-backpack")
    assert inventory.product_is_added("sauce-labs-backpack")

    inventory.open_cart()

    cart = CartPage(page)
    assert cart.item_count() > 0
    cart.go_to_checkout()

    info = CheckoutYourInformationPage(page)
    info.fill_info_and_continue("John", "Doe", "12345")

    overview = CheckoutOverviewPage(page)
    overview.finish_checkout()

    complete = CheckoutCompletePage(page)
    assert complete.is_complete()