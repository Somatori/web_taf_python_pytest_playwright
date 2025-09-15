from pages.login_page import LoginPage
from model.user import User

def test_standard_user_can_login(page):
    """
    Smoke test: open saucedemo, log in as standard_user and assert inventory is shown.
    """
    user = User(username="standard_user", password="secret_sauce")
    login = LoginPage(page)
    login.goto()
    login.login(user.username, user.password)

    # simple assertion: inventory list visible or URL includes inventory
    assert "inventory.html" in page.url or page.locator(".inventory_list").is_visible()
