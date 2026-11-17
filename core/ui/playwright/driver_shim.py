import time
from typing import Any, List, Optional, Union
from playwright.sync_api import Page, Locator
from core.ui.playwright.locator_converter import convert_selenium_locator_to_playwright


class PlaywrightWebElementShim:
    """
    Shims a Playwright Locator to mimic Selenium's WebElement interface.
    This allows existing Selenium-oriented action classes (ClickActions,
    SendKeysActions, ElementsActions, etc.) to interact directly with Playwright.
    """

    def __init__(self, locator: Locator, page: Page):
        self._locator = locator
        self._page = page

    def click(self):
        self._locator.click()

    def send_keys(self, *values):
        text = "".join(str(v) for v in values)
        # Playwright fill clears, or type appends
        self._locator.fill(text)

    def clear(self):
        self._locator.fill("")

    @property
    def text(self) -> str:
        return self._locator.inner_text()

    def get_attribute(self, name: str) -> Optional[str]:
        if name == "value":
            return self._locator.input_value()
        return self._locator.get_attribute(name)

    def is_displayed(self) -> bool:
        return self._locator.is_visible()

    def is_enabled(self) -> bool:
        return self._locator.is_enabled()

    def is_selected(self) -> bool:
        return self._locator.is_checked()

    @property
    def tag_name(self) -> str:
        return str(self._locator.evaluate("el => el.tagName.toLowerCase()"))

    @property
    def size(self) -> dict:
        box = self._locator.bounding_box()
        return {"width": box["width"], "height": box["height"]} if box else {"width": 0, "height": 0}

    @property
    def location(self) -> dict:
        box = self._locator.bounding_box()
        return {"x": box["x"], "y": box["y"]} if box else {"x": 0, "y": 0}


class PlaywrightWebDriverShim:
    """
    Shims a Playwright Page instance to fully satisfy Selenium's WebDriver interface
    required by BaseApp, BasePage, UIElement, and BaseTest.
    """

    def __init__(self, page: Page, browser_name: str = "chromium"):
        self.page = page
        self.browser_name = browser_name
        self.is_playwright_shim = True

    # -------------------------------------------------------------------------
    # Navigation & URL Properties
    # -------------------------------------------------------------------------
    def get(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    @property
    def current_window_handle(self) -> str:
        return "main"

    @property
    def window_handles(self) -> List[str]:
        return ["main"]

    def refresh(self):
        self.page.reload()

    def back(self):
        self.page.go_back()

    def forward(self):
        self.page.go_forward()

    # -------------------------------------------------------------------------
    # Element Search
    # -------------------------------------------------------------------------
    def find_element(self, by: str, value: str) -> PlaywrightWebElementShim:
        pw_selector = convert_selenium_locator_to_playwright((by, value))
        loc = self.page.locator(pw_selector).first
        # Wait for attached / present
        loc.wait_for(state="attached", timeout=10000)
        return PlaywrightWebElementShim(loc, self.page)

    def find_elements(self, by: str, value: str) -> List[PlaywrightWebElementShim]:
        pw_selector = convert_selenium_locator_to_playwright((by, value))
        count = self.page.locator(pw_selector).count()
        return [PlaywrightWebElementShim(self.page.locator(pw_selector).nth(i), self.page) for i in range(count)]

    # -------------------------------------------------------------------------
    # JavaScript Execution
    # -------------------------------------------------------------------------
    def execute_script(self, script: str, *args) -> Any:
        # If any arg is our WebElementShim, unwrap to JS handle
        pw_script = f"() => {{ {script} }}" if not script.strip().startswith("return") else f"() => {{ {script}; }}"
        try:
            return self.page.evaluate(script)
        except Exception:
            # Fallback simple eval
            return self.page.evaluate(f"() => {{ return {script.replace('return ', '')} }}")

    # -------------------------------------------------------------------------
    # Window & Session Lifecycle
    # -------------------------------------------------------------------------
    def maximize_window(self):
        """Maximizes the browser window via native CDP command or available screen size."""
        try:
            session = self.page.context.new_cdp_session(self.page)
            res = session.send("Browser.getWindowForTarget")
            window_id = res.get("windowId")
            if window_id:
                session.send("Browser.setWindowBounds", {
                    "windowId": window_id,
                    "bounds": {"windowState": "maximized"}
                })
                session.detach()
                return
        except Exception:
            pass

        try:
            screen_size = self.page.evaluate("() => ({ width: window.screen.availWidth, height: window.screen.availHeight })")
            if screen_size and screen_size.get("width") and screen_size.get("height"):
                self.page.set_viewport_size({"width": screen_size["width"], "height": screen_size["height"]})
        except Exception:
            pass

    def set_window_size(self, width: int, height: int):
        self.page.set_viewport_size({"width": width, "height": height})

    def get_window_size(self) -> dict:
        vp = self.page.viewport_size or {"width": 1366, "height": 768}
        return vp

    def get_screenshot_as_png(self) -> bytes:
        return self.page.screenshot(full_page=False)

    def save_screenshot(self, filename: str) -> bool:
        self.page.screenshot(path=filename, full_page=False)
        return True

    def quit(self):
        from core.ui.playwright.driver_factory import PlaywrightDriverFactory
        PlaywrightDriverFactory.close_all()

    def close(self):
        self.page.close()

    # -------------------------------------------------------------------------
    # Cookies & Context
    # -------------------------------------------------------------------------
    def get_cookies(self) -> List[dict]:
        return self.page.context.cookies()

    def get_cookie(self, name: str) -> Optional[dict]:
        for c in self.page.context.cookies():
            if c.get("name") == name:
                return c
        return None

    def add_cookie(self, cookie_dict: dict):
        if "url" not in cookie_dict:
            cookie_dict["url"] = self.page.url
        self.page.context.add_cookies([cookie_dict])

    def delete_cookie(self, name: str):
        cookies = [c for c in self.page.context.cookies() if c.get("name") != name]
        self.page.context.clear_cookies()
        if cookies:
            self.page.context.add_cookies(cookies)

    def delete_all_cookies(self):
        self.page.context.clear_cookies()
