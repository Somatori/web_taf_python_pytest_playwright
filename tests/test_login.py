from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_standard_user_can_login(page, credentials):
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    inventory = InventoryPage(page)
    assert inventory.inventory_list().is_visible()