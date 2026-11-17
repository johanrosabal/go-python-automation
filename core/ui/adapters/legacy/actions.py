"""
Legacy Actions Compatibility Interpreter.
Translates legacy fluent builder action chains (e.g., self.click().set_locator().single_click())
into the modern framework's high-performance dual-engine (UIElement, Selenium & Playwright).
"""
import time
from typing import Optional, Union, Tuple, Any
from core.ui.actions.ui_element import UIElement
from core.ui.common.base_app import BaseApp


def _create_ui_element(driver, locator: Optional[Tuple], page: str = "Page", timeout: int = 10) -> Optional[UIElement]:
    """Helper to convert a legacy 2-tuple or 3-tuple locator into an active UIElement."""
    if not locator:
        return None
    by = locator[0]
    selector = locator[1]
    label = locator[2] if len(locator) > 2 else f"{by}:{selector}"
    
    active_driver = driver or BaseApp.get_driver()
    if not active_driver:
        return None
        
    element = UIElement(driver=active_driver, locator=(by, selector), locator_name=label)
    if timeout:
        element.at(timeout)
    return element


class LegacyClick:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None
        self._page = "Page"
        self._locator = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        self._page = page
        self._locator = locator
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def set_element(self, element):
        self._element = element
        return self

    def single_click(self):
        if self._element:
            self._element.click()
        return self

    def double_click(self):
        if self._element:
            self._element.double_click()
        return self

    def right_click(self):
        if self._element:
            self._element.right_click()
        return self

    def hover(self):
        if self._element:
            self._element.hover()
        return self

    def pause(self, seconds: int = 1):
        time.sleep(seconds)
        return self

    def screenshot(self):
        if self._element:
            self._element.screenshot(self._element.locator_name or "Click Screenshot")
        return self


class LegacySendKeys:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None
        self._page = "Page"
        self._locator = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        self._page = page
        self._locator = locator
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def set_text(self, text: str):
        if self._element:
            self._element.type(text)
        return self

    def highlight(self):
        return self

    def clear(self):
        if self._element:
            self._element.clear()
        return self

    def set_encrypt(self):
        return self

    def press_enter(self):
        if self._element:
            self._element.press_enter()
        return self

    def press_tab(self):
        if self._element:
            self._element.press_tab()
        return self

    def press_escape(self):
        if self._element:
            self._element.press_escape()
        return self


class LegacyGetText:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None
        self._page = "Page"
        self._locator = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        self._page = page
        self._locator = locator
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def by_text(self) -> str:
        if self._element:
            return self._element.get_text() or ""
        return ""

    def by_attribute(self, attribute_name: str) -> str:
        if self._element:
            return self._element.get_attribute(attribute_name) or ""
        return ""

    def contains(self, text: str) -> bool:
        if self._element:
            return self._element.contains_text(text)
        return False

    def get_trimmed(self) -> str:
        if self._element:
            return self._element.get_trimmed_text() or ""
        return ""


class LegacyNavigation:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()

    def go(self, base_url: str = "", relative_url: str = ""):
        driver = self._driver or BaseApp.get_driver()
        if not base_url:
            base_url = BaseApp.get_base_url()
        url = base_url.rstrip("/") + "/" + relative_url.lstrip("/") if base_url else relative_url
        if driver:
            driver.get(url)
        return self

    def get_current_url(self) -> str:
        driver = self._driver or BaseApp.get_driver()
        return driver.current_url if driver else ""

    def refresh(self):
        driver = self._driver or BaseApp.get_driver()
        if driver:
            driver.refresh()
        return self

    def back(self):
        driver = self._driver or BaseApp.get_driver()
        if driver:
            driver.back()
        return self

    def forward(self):
        driver = self._driver or BaseApp.get_driver()
        if driver:
            driver.forward()
        return self


class LegacyScreenshot:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None
        self._description = "Screenshot"

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def save_highlight(self, description: str = "Screenshot"):
        self._description = description
        if self._element:
            self._element.screenshot(description)
        else:
            driver = self._driver or BaseApp.get_driver()
            if driver:
                import allure
                try:
                    allure.attach(driver.get_screenshot_as_png(), name=description, attachment_type=allure.attachment_type.PNG)
                except Exception:
                    pass
        return self

    def add_comment(self, comment: str):
        import allure
        allure.attach(comment, name="Legacy Step Comment", attachment_type=allure.attachment_type.TEXT)
        return self

    def screenshot(self):
        return self.save_highlight("Step Screenshot")


class LegacyDropdown:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def select_by_text(self, text: str):
        if self._element:
            self._element.select_by_text(text)
        return self

    def select_by_value(self, value: str):
        if self._element:
            self._element.select_by_value(value)
        return self

    def select_by_index(self, index: int):
        if self._element:
            self._element.select_by_index(index)
        return self

    def get_selected_text(self) -> str:
        if self._element:
            return self._element.get_selected_text() or ""
        return ""


class LegacyCheckbox:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def check(self, state: bool = True):
        if self._element:
            self._element.check(state)
        return self

    def is_checked(self) -> bool:
        if self._element:
            return self._element.is_checked()
        return False


class LegacyRadio:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def select_radio(self):
        if self._element:
            self._element.select_radio()
        return self

    def is_selected(self) -> bool:
        if self._element:
            return self._element.is_selected()
        return False


class LegacyTable:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def get_row_count(self) -> int:
        if self._element:
            return self._element.get_row_count()
        return 0

    def get_cell_text(self, row: int, col: Union[int, str]) -> str:
        if self._element:
            return self._element.get_cell_text(row, col)
        return ""

    def get_table_data(self):
        if self._element:
            return self._element.get_table_data()
        return []


class LegacyAlert:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()

    def accept(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("alert", self._driver).accept()
        return self

    def dismiss(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("alert", self._driver).dismiss()
        return self

    def get_text(self) -> str:
        from core.ui.actions.factory import ActionFactory
        return ActionFactory.create("alert", self._driver).get_text()


class LegacyFrame:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()

    def switch_to(self, locator: Tuple):
        from core.ui.actions.factory import ActionFactory
        by, sel = locator[0], locator[1]
        ActionFactory.create("frame", self._driver).to_frame((by, sel))
        return self

    def switch_to_default(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("frame", self._driver).to_default()
        return self


class LegacySwitchWindow:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()

    def switch_to_new(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("switch_windows", self._driver).switch_to_new()
        return self

    def to_tab(self, index: int):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("switch_windows", self._driver).to_tab(index)
        return self

    def close_current(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("switch_windows", self._driver).close_current()
        return self


class LegacyUploadFile:
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: Optional[Tuple] = None, page: str = "Page", explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def upload(self, file_path: str):
        if self._element:
            self._element.upload_file(file_path)
        return self


class LegacyElement:
    """Legacy Element helper and fluent wrapper."""
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None
        self._locator = None

    def set_locator(self, locator: tuple, page: str = 'Page', explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        self._locator = locator
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def set_element(self, element):
        self._element = element
        return self

    def is_visible(self) -> bool:
        if self._element:
            return self._element.is_visible()
        return False

    def is_not_visible(self, locator: Optional[Tuple] = None, timeout: int = 5) -> bool:
        if locator:
            el = _create_ui_element(self._driver, locator, timeout=timeout)
            return el.is_not_visible() if el else True
        if self._element:
            return self._element.is_not_visible()
        return True

    def is_enabled(self) -> bool:
        if self._element:
            return self._element.is_enabled()
        return False

    def is_clickable(self) -> bool:
        if self._element:
            return self._element.is_clickable()
        return False

    def get_element(self, locator: Optional[Tuple] = None, timeout: int = 10):
        if locator:
            return _create_ui_element(self._driver, locator, timeout=timeout)
        return self._element

    @staticmethod
    def wait_for_element(driver=None, locator=None, timeout: int = 10):
        driver = driver or BaseApp.get_driver()
        if locator:
            return _create_ui_element(driver, locator, timeout=timeout)
        return None

    @staticmethod
    def wait_for_element_clickable(driver=None, locator=None, timeout: int = 10):
        driver = driver or BaseApp.get_driver()
        if locator:
            el = _create_ui_element(driver, locator, timeout=timeout)
            if el:
                el.wait_clickable()
            return el
        return None

    @staticmethod
    def wait_for_element_visible(driver=None, locator=None, timeout: int = 10):
        driver = driver or BaseApp.get_driver()
        if locator:
            el = _create_ui_element(driver, locator, timeout=timeout)
            if el:
                el.wait_visible()
            return el
        return None

    @staticmethod
    def wait_for_element_present(driver=None, locator=None, timeout: int = 10):
        driver = driver or BaseApp.get_driver()
        if locator:
            el = _create_ui_element(driver, locator, timeout=timeout)
            if el:
                el.wait_present()
            return el
        return None

    @staticmethod
    def log_console(page: str, action: str, locator: tuple) -> str:
        label = locator[2] if len(locator) > 2 else f"{locator[0]}:{locator[1]}"
        return f"[{page}] [{action}] -> {label}"


class LegacyScroll:
    """Legacy Scroll actions shim."""
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: tuple, page: str = 'Page', explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def set_element(self, element=None):
        self._element = element
        return self

    def pause(self, seconds: int):
        BaseApp.pause(seconds)
        return self

    def to_bottom(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("scroll", self._driver).to_bottom()
        return self

    def to_top(self):
        from core.ui.actions.factory import ActionFactory
        ActionFactory.create("scroll", self._driver).to_top()
        return self

    def to_center(self):
        if self._element:
            self._element.scroll_to_center()
        return self

    def to_element(self, pixels: int = 0):
        if self._element:
            self._element.scroll_to()
        return self


class LegacyElementHighlighter:
    """Legacy Element Highlighter shim."""
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self._element: Optional[UIElement] = None

    def set_locator(self, locator: tuple, page: str = 'Page', explicit_wait: int = 10):
        self._driver = self._driver or BaseApp.get_driver()
        if locator:
            self._element = _create_ui_element(self._driver, locator, page, explicit_wait)
        return self

    def set_element(self, element=None):
        self._element = element
        return self

    def highlight_element(self, color: str = "red", border_width: str = "3px"):
        if self._element:
            try:
                self._element.highlight(color=color, border_width=border_width)
            except Exception:
                pass
        return self

    def highlight_remove(self):
        if self._element:
            try:
                self._element.unhighlight()
            except Exception:
                pass
        return self

    def highlight_temporarily(self, duration: float = 0.5, color: str = "red", border_width: str = "3px"):
        self.highlight_element(color=color, border_width=border_width)
        time.sleep(duration)
        self.highlight_remove()
        return self


class LegacyVerifyLocators:
    """Legacy VerifyLocators shim."""
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()

    def verify_page_locators(self, locators: list) -> list:
        missing = []
        for loc in locators:
            by, val = loc[0], loc[1]
            desc = loc[2] if len(loc) > 2 else f"{by}:{val}"
            el = _create_ui_element(self._driver, (by, val), timeout=5)
            if not el or not el.is_visible():
                missing.append(desc)
        return missing



