# pages/base_page.py
from typing import Any, Dict, Tuple, Union
from playwright.sync_api import Page, Locator, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def _to_locator(self, sel_or_locator: Union[str, Locator, Tuple, Dict]) -> Locator:
        """
        Normalize input into a Playwright Locator.

        Accepted forms:
          - Locator -> returned as-is
          - selector string -> page.locator(selector)  (CSS by default; engine-prefixed strings supported)
          - dict form for role lookup: {"role": "button", "name": "Save", "exact": True}
          - tuple form for role lookup: ("role", "button", {"name": "Save"})
        """
        # already a Locator (duck-type)
        if hasattr(sel_or_locator, "click"):
            return sel_or_locator  # type: ignore

        # dict form for role
        if isinstance(sel_or_locator, dict):
            if "role" in sel_or_locator:
                role = sel_or_locator["role"]
                kwargs = {k: v for k, v in sel_or_locator.items() if k != "role"}
                return self.page.get_by_role(role, **kwargs)
            raise ValueError("Unsupported dict selector. Use {'role': ..., 'name': ...} for role lookups.")

        # tuple/list form
        if isinstance(sel_or_locator, (list, tuple)) and len(sel_or_locator) >= 2:
            engine = sel_or_locator[0]
            if engine == "role":
                role = sel_or_locator[1]
                kwargs = {}
                if len(sel_or_locator) >= 3 and isinstance(sel_or_locator[2], dict):
                    kwargs = sel_or_locator[2]
                return self.page.get_by_role(role, **kwargs)
            raise ValueError(f"Unsupported tuple selector engine: {engine}")

        # fallback: treat as selector string (CSS by default)
        if isinstance(sel_or_locator, str):
            return self.page.locator(sel_or_locator)

        raise TypeError(f"Unsupported selector type: {type(sel_or_locator)!r}")

    def click(self, sel_or_locator: Any, timeout: int = 5000, force: bool = False):
        loc = self._to_locator(sel_or_locator)
        try:
            loc.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        expect(loc).to_be_enabled(timeout=timeout)
        loc.click(timeout=timeout, force=force)

    def fill(self, sel_or_locator: Any, text: str, timeout: int = 5000):
        loc = self._to_locator(sel_or_locator)
        loc.wait_for(state="visible", timeout=timeout)
        loc.fill(text, timeout=timeout)

    def text(self, sel_or_locator: Any) -> str | None:
        loc = self._to_locator(sel_or_locator)
        return loc.text_content()

    def is_visible(self, sel_or_locator: Any) -> bool:
        loc = self._to_locator(sel_or_locator)
        try:
            return loc.is_visible()
        except Exception:
            return False
