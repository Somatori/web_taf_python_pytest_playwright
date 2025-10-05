from typing import Any
from playwright.sync_api import Page, Locator, expect


class BasePage:
    """
    Minimalistic BasePage that expects callers to pass Locator objects.
    Pages should expose locator-returning methods/properties, e.g.:

        def save_button(self):
            return self.page.get_by_test_id("save-company-settings")

    Then call: self.click(self.save_button())
    """

    def __init__(self, page: Page):
        self.page = page

    def _ensure_locator(self, loc_like: Any) -> Locator:
        """
        Ensure the passed object behaves like a Playwright Locator.
        Accepts Locator or any object that exposes click/fill/text_content methods.
        Raises TypeError for unsupported types.
        """
        # Duck-typing: Locator and Locator-like objects have click/fill/text_content
        if hasattr(loc_like, "click") and hasattr(loc_like, "wait_for"):
            return loc_like  # type: ignore
        raise TypeError(
            "BasePage methods expect a Playwright Locator (or Locator-like) object. "
            "Pages must expose locator-returning methods, e.g. def save_button(self): return self.page.locator(...)."
        )

    def click(self, locator_like: Any, timeout: int = 5000, force: bool = False):
        loc = self._ensure_locator(locator_like)
        try:
            loc.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        expect(loc).to_be_enabled(timeout=timeout)
        loc.click(timeout=timeout, force=force)

    def fill(self, locator_like: Any, text: str, timeout: int = 5000):
        loc = self._ensure_locator(locator_like)
        loc.wait_for(state="visible", timeout=timeout)
        loc.fill(text, timeout=timeout)

    def text(self, locator_like: Any) -> str | None:
        loc = self._ensure_locator(locator_like)
        return loc.text_content()

    def is_visible(self, locator_like: Any) -> bool:
        loc = self._ensure_locator(locator_like)
        try:
            return loc.is_visible()
        except Exception:
            return False

    def screenshot(self, path: str, **kwargs):
        """
        Helper that delegates to page.screenshot (keeps API available).
        If you want per-locator screenshots, pass locator and use locator.screenshot().
        """
        return self.page.screenshot(path=path, **kwargs)