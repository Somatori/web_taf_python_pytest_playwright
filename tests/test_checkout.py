from pages.login_page import LoginPage
from pages.checkout_page import InventoryPage, CartPage, CheckoutYourInformationPage, CheckoutOverviewPage, CheckoutCompletePage


def test_add_item_and_checkout(page, credentials):
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    inventory = InventoryPage(page)
    # add product by id used in saucedemo (example)
    inventory.product_add_button("sauce-labs-backpack").click()

    inventory.cart_button().click()

    cart = CartPage(page)
    cart.checkout_button().click()

    info = CheckoutYourInformationPage(page)
    info.fill(info.first_name_input(), "John")
    info.fill(info.last_name_input(), "Doe")
    info.fill(info.postal_code_input(), "12345")
    info.click(info.continue_button())

    overview = CheckoutOverviewPage(page)
    overview.click(overview.finish_button())

    complete = CheckoutCompletePage(page)
    assert complete.complete_header().is_visible()
