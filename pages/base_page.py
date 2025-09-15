class BasePage:
    """
    Minimal Page Object base class providing light wrappers around Playwright page.
    """

    def __init__(self, page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url)

    def click(self, selector: str, **kwargs):
        self.page.click(selector, **kwargs)

    def fill(self, selector: str, text: str, **kwargs):
        self.page.fill(selector, text, **kwargs)

    def get_text(self, selector: str) -> str | None:
        return self.page.text_content(selector)

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def wait_for_selector(self, selector: str, timeout: int = 5000):
        return self.page.wait_for_selector(selector, timeout=timeout)

    def screenshot(self, path: str, **kwargs):
        return self.page.screenshot(path=path, **kwargs)
