from pages.login_page import LoginPage

def test_standard_user_can_login(page, credentials):
    """
    Smoke test: open saucedemo, log in using credentials from env and assert inventory is shown.
    """
    login = LoginPage(page)
    login.goto()
    login.login(credentials.username, credentials.password)

    assert "inventory.html" in page.url or page.locator(".inventory_list").is_visible()

