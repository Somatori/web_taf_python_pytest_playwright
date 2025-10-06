from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutYourInformationPage, CheckoutOverviewPage, CheckoutCompletePage


def test_add_item_and_checkout(page, credentials):
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    inventory = InventoryPage(page)
    # add product by id used in saucedemo (example)
    inventory.product_add_button("sauce-labs-backpack").click()

    # open cart
    inventory.cart_button().click()

    cart = CartPage(page)
    cart.checkout_button().click()

    info = CheckoutYourInformationPage(page)
    info.first_name_input().fill("John")
    info.last_name_input().fill("Doe")
    info.postal_code_input().fill("12345")
    info.continue_button().click()

    overview = CheckoutOverviewPage(page)
    overview.finish_button().click()

    complete = CheckoutCompletePage(page)
    assert complete.complete_header().is_visible()