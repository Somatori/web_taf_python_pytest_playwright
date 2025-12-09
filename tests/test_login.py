import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_standard_user_can_login(page, credentials):
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    inventory = InventoryPage(page)
    assert inventory.is_inventory_visible()
    assert False
