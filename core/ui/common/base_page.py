from typing import Dict, Any, List, Self
from core.ui.common.base_app import BaseApp
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.ui.actions.selenium import (
    ClickActions,
    SendKeysActions,
    ScrollActions,
    DropdownActions,
    ElementsActions,
    NavigationActions,
    SwitchWindowsActions,
    FrameActions,
    RadioActions,
    ScreenshotActions,
    AlertActions,
    CookieActions,
    DiagnosticsActions,
    ScriptActions,
    StorageActions,
)
from core.ui.actions.ui_element import UIElement
from core.ui.common.singleton import SingletonMeta
from selenium.webdriver.remote.webdriver import WebDriver

# Advanced Utilities
from core.utils.visual_comparer import VisualComparer
from core.utils.accessibility_tester import AccessibilityTester
from core.utils.performance_monitor import PerformanceMonitor


class BasePage(BaseApp, metaclass=SingletonMeta):
    """
    Foundational Base class for all Page Objects within the framework.

    Inherits from `BaseApp` and implements the `SingletonMeta` pattern to
    ensure efficient instance reuse across tests. It serves as a central
    aggregator for specialized action components, providing a fluent and
    unified interface for UI automation.

    Attributes:
        click (ClickActions): Handler for all mouse-related interactions.
        send_keys (SendKeysActions): Handler for keyboard and text input.
        scroll (ScrollActions): Handler for viewport and element scrolling.
        select (DropdownActions): Handler for standard HTML dropdowns.
        elements (ElementsActions): Handler for element state checks (visibility, etc.).
        navigation (NavigationActions): Handler for browser-level navigation.
        window (SwitchWindowsActions): Handler for window and tab management.
        radio (RadioActions): Handler for radio button interactions.
        screenshot (ScreenshotActions): Handler for screen capture.
        frame (FrameActions): Handler for IFrame context switching.
    """

    # Explicit Type Hints for IDE Autocomplete (Pylance / PyCharm)
    click: ClickActions
    send_keys: SendKeysActions
    scroll: ScrollActions
    select: DropdownActions
    elements: ElementsActions
    navigation: NavigationActions
    window: SwitchWindowsActions
    radio: RadioActions
    screenshot: ScreenshotActions
    frame: FrameActions
    alert: AlertActions

    def __init__(self, driver: WebDriver = None):
        """
        Initializes the Page Object with lazy-loaded action components.

        Args:
            driver (WebDriver, optional): The Selenium WebDriver instance.
                Defaults to the global driver managed by BaseApp.
        """
        self._page_action_cache = {}

    def _get_page_action(self, key: str, cls, pass_driver: bool = True):
        if key not in self._page_action_cache:
            if pass_driver:
                from core.ui.actions.factory import ActionFactory
                try:
                    self._page_action_cache[key] = ActionFactory.create(key, self.driver)
                except Exception:
                    self._page_action_cache[key] = cls(self.driver)
            else:
                self._page_action_cache[key] = cls()
        return self._page_action_cache[key]

    @property
    def wait(self) -> WebDriverWait:
        return self._get_page_action("wait", lambda d: WebDriverWait(d, 10))

    @property
    def click(self) -> ClickActions:
        return self._get_page_action("click", ClickActions)

    @property
    def send_keys(self) -> SendKeysActions:
        return self._get_page_action("send_keys", SendKeysActions)

    @property
    def scroll(self) -> ScrollActions:
        return self._get_page_action("scroll", ScrollActions)

    @property
    def select(self) -> DropdownActions:
        return self._get_page_action("select", DropdownActions)

    @property
    def elements(self) -> ElementsActions:
        return self._get_page_action("elements", ElementsActions)

    @property
    def navigation(self) -> NavigationActions:
        return self._get_page_action("navigation", NavigationActions)

    @property
    def window(self) -> SwitchWindowsActions:
        return self._get_page_action("window", SwitchWindowsActions)

    @property
    def radio(self) -> RadioActions:
        return self._get_page_action("radio", RadioActions)

    @property
    def screenshot(self) -> ScreenshotActions:
        return self._get_page_action("screenshot", ScreenshotActions)

    @property
    def frame(self) -> FrameActions:
        return self._get_page_action("frame", FrameActions)

    @property
    def alert(self) -> AlertActions:
        return self._get_page_action("alert", AlertActions)

    @property
    def cookies(self) -> CookieActions:
        """Handler for browser cookie management (get, add, delete, inspect)."""
        return self._get_page_action("cookies", CookieActions)

    @property
    def storage(self) -> StorageActions:
        """Handler for HTML5 Web Storage (localStorage & sessionStorage)."""
        return self._get_page_action("storage", StorageActions)

    @property
    def script(self) -> ScriptActions:
        """Handler for clean JavaScript execution and Promise evaluation."""
        return self._get_page_action("script", ScriptActions)

    @property
    def diagnostics(self) -> DiagnosticsActions:
        """Handler for browser console errors, warnings, and JS diagnostics."""
        return self._get_page_action("diagnostics", DiagnosticsActions)

    @property
    def visual(self) -> VisualComparer:
        return self._get_page_action("visual", VisualComparer, pass_driver=False)

    @property
    def a11y(self) -> AccessibilityTester:
        return self._get_page_action("a11y", AccessibilityTester)

    @property
    def performance(self) -> PerformanceMonitor:
        return self._get_page_action("performance", PerformanceMonitor)

    def element(self, locator: tuple) -> UIElement:
        """
        Creates a `UIElement` facade for fluent interaction with a specific locator.

        This is the recommended way to perform actions on elements contextually
        within a Page Object.

        Args:
            locator (tuple): The (By, Value) locator of the element.

        Returns:
            UIElement: A facade instance bound to the locator and this page.
        """
        return UIElement(self.driver, locator, page_object=self)

    # --- God Tier Advanced Methods ---

    PAGE_PATH: str = ""
    _page_anchors: List[str] = []
    _IGNORED_FORM_KEYS = {
        "description", "expected_error", "expected_results",
        "test_id", "id", "scenario", "error_key", "expected_url",
    }

    def assert_visual_match(self, test_name: str, threshold: float = 0.01) -> Self:
        """
        Performs a visual comparison of the current page against a baseline.
        The validation only runs if 'visual.enable' is True in the configuration.
        """
        enabled = self.config.get("visual.enable", True)

        if not enabled:
            self.logger.warning(
                f"Visual validation skipped for '{test_name}' (Disabled in config)."
            )
            return self

        self.screenshot.full_page(f"temp_visual_{test_name}")
        current_screenshot = self.screenshot.last_filepath
        match = self.visual.compare(current_screenshot, test_name, threshold)
        assert (
            match
        ), f"Visual regression detected for {test_name}. Check reports/visual/diffs/"
        return self

    def assert_no_accessibility_violations(self, impact_level: str = "critical") -> Self:
        """
        Scans the page and fails if violations are found.
        """
        self.a11y.assert_no_violations(self.__class__.__name__, impact_level)
        return self

    def capture_performance_metrics(self):
        """
        Extracts and logs browser performance data.
        """
        return self.performance.capture_metrics(self.__class__.__name__)

    # --- Navigation & Page Readiness Contract ---

    def open(self, url: str = None) -> Self:
        """
        Navigates to the specified URL, or to `base_url + PAGE_PATH` if defined.
        Automatically awaits network idle after page load.

        Args:
            url (str, optional): Target URL. If None, uses web.base_url (+ PAGE_PATH).

        Returns:
            Self: The current Page Object instance for fluent chaining.
        """
        if url:
            target = url
        elif self.PAGE_PATH:
            target = f"{self.base_url.rstrip('/')}/{self.PAGE_PATH.lstrip('/')}"
        else:
            target = self.base_url
        self.navigation.open(target)
        self.window.set_zoom_level(75)
        self.wait_network_idle(timeout=5, idle_time=0.2)
        return self

    def open_relative(self, path: str) -> Self:
        """
        Navigates to a path relative to the base URL.
        Automatically awaits network idle after navigation.

        Args:
            path (str): Relative path (e.g. "/inventory").

        Returns:
            Self: The current Page Object instance for fluent chaining.
        """
        self.navigation.go(path)
        self.wait_network_idle(timeout=5, idle_time=0.2)
        return self

    def is_loaded(self) -> bool:
        """
        Verifies if the page is loaded by checking `PAGE_PATH` in the current URL
        and ensuring all locators marked with `anchor=True` are visible.
        """
        if self.PAGE_PATH and self.PAGE_PATH not in self.driver.current_url:
            return False
        for anchor_attr in getattr(self, "_page_anchors", []):
            element = getattr(self, anchor_attr, None)
            if element is not None and not element.is_visible():
                return False
        return True

    def wait_network_idle(self, timeout: int = 10, idle_time: float = 0.3) -> Self:
        """
        Waits for in-flight asynchronous network activity (Fetch & XMLHttpRequest) 
        to settle and reach zero active connections for a sustained duration.

        Args:
            timeout (int): Maximum total seconds to wait for network stability. Defaults to 10.
            idle_time (float): Sustained silence period (seconds) with 0 active requests required. Defaults to 0.3.

        Returns:
            Self: The current Page Object instance for fluent chaining.
        """
        import time
        script_install = """
        if (!window.__agyNetworkTrackerInstalled) {
            window.__agyNetworkTrackerInstalled = true;
            window.__agyActiveRequests = 0;
            
            var origOpen = XMLHttpRequest.prototype.open;
            var origSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.open = function() {
                this._agyTracked = true;
                return origOpen.apply(this, arguments);
            };
            XMLHttpRequest.prototype.send = function() {
                if (this._agyTracked) {
                    window.__agyActiveRequests = (window.__agyActiveRequests || 0) + 1;
                    var onDone = function() {
                        if (this._agyDone) return;
                        this._agyDone = true;
                        window.__agyActiveRequests = Math.max(0, (window.__agyActiveRequests || 1) - 1);
                    };
                    this.addEventListener('load', onDone);
                    this.addEventListener('error', onDone);
                    this.addEventListener('abort', onDone);
                    this.addEventListener('timeout', onDone);
                }
                return origSend.apply(this, arguments);
            };

            if (window.fetch) {
                var origFetch = window.fetch;
                window.fetch = function() {
                    window.__agyActiveRequests = (window.__agyActiveRequests || 0) + 1;
                    return origFetch.apply(this, arguments)
                        .then(function(res) {
                            window.__agyActiveRequests = Math.max(0, (window.__agyActiveRequests || 1) - 1);
                            return res;
                        })
                        .catch(function(err) {
                            window.__agyActiveRequests = Math.max(0, (window.__agyActiveRequests || 1) - 1);
                            throw err;
                        });
                };
            }
        }
        """
        try:
            self.driver.execute_script(script_install)
        except Exception:
            return self

        start_time = time.time()
        consecutive_idle_start = None

        while (time.time() - start_time) < timeout:
            try:
                status = self.driver.execute_script("""
                    return {
                        active: window.__agyActiveRequests || 0,
                        ready: document.readyState
                    };
                """)
                active = status.get("active", 0) if status else 0
                ready = status.get("ready", "complete") if status else "complete"

                if active == 0 and ready in ("interactive", "complete"):
                    if consecutive_idle_start is None:
                        consecutive_idle_start = time.time()
                    elif (time.time() - consecutive_idle_start) >= idle_time:
                        return self
                else:
                    consecutive_idle_start = None
            except Exception:
                pass
            time.sleep(0.05)

        return self

    def wait_until_loaded(self, timeout: int = None, wait_network: bool = True) -> Self:
        """
        Explicitly waits for in-flight network activity, `PAGE_PATH` (if set), 
        and all `anchor=True` elements to become visible.

        Args:
            timeout (int, optional): Maximum timeout per check.
            wait_network (bool): Whether to wait for network idle first. Defaults to True.

        Returns:
            Self: The current Page Object instance for fluent chaining.
        """
        if wait_network:
            self.wait_network_idle(timeout=timeout or 5, idle_time=0.2)

        if self.PAGE_PATH:
            self.navigation.wait_url_contains(self.PAGE_PATH, timeout=timeout or 10)
        for anchor_attr in getattr(self, "_page_anchors", []):
            element = getattr(self, anchor_attr, None)
            if element is not None:
                if timeout:
                    element.at(timeout).wait_visible()
                else:
                    element.wait_visible()
        return self

    # --- Smart Data-Driven Form Orchestration (Layer 3 -> Layer 2) ---

    def fill_form(self, data: Dict[str, Any], strict: bool = False) -> Self:
        """
        Automatically populates a form from a dictionary (either `self.get_data_for_test()` / `self.test_data`
        or the full JSON containing `tests.data`) by invoking the Page Object's own granular Layer-2
        atomic methods: `set_<field>`, `select_<field>`, `check_<field>` / `uncheck_<field>`, or `upload_<field>`.

        Args:
            data (Dict[str, Any]): Dictionary of field keys and values to populate.
            strict (bool): If True, raises AttributeError when a key has no matching atomic method.

        Returns:
            Self: The current Page Object instance for fluent chaining.
        """
        if not isinstance(data, dict):
            return self

        # Support both full JSON structure {"tests": {"data": {...}}} and unwrapped {"username": "..."}
        if "tests" in data and isinstance(data["tests"], dict) and isinstance(data["tests"].get("data"), dict):
            payload = dict(data["tests"]["data"])
        elif "data" in data and isinstance(data["data"], dict) and len(data) <= 3:
            payload = dict(data["data"])
        else:
            payload = dict(data)

        # Role-Based User Resolution: if `"role"` is present and there is no `set_role`/`select_role`,
        # automatically expand `username` and `password` from `users.roles.<role>` if not explicitly overridden
        if "role" in payload and not hasattr(self, "set_role") and not hasattr(self, "select_role"):
            role_name = payload.pop("role")
            if role_name:
                role_creds = self.get_user(role_name)
                if "username" not in payload and role_creds.get("username") is not None:
                    payload["username"] = role_creds["username"]
                if "password" not in payload and role_creds.get("password") is not None:
                    payload["password"] = role_creds["password"]

        for field_key, value in payload.items():
            if field_key in self._IGNORED_FORM_KEYS or value is None:
                continue

            # 1. Boolean values -> check_<field>() / uncheck_<field>() or set_<field>(bool)
            if isinstance(value, bool):
                bool_method_name = f"check_{field_key}" if value else f"uncheck_{field_key}"
                if hasattr(self, bool_method_name) and callable(getattr(self, bool_method_name)):
                    getattr(self, bool_method_name)()
                    continue
                if hasattr(self, f"set_{field_key}") and callable(getattr(self, f"set_{field_key}")):
                    getattr(self, f"set_{field_key}")(value)
                    continue

            # 2. Standard atomic methods: set_<field>, enter_<field>, select_<field>, upload_<field>
            matched = False
            for prefix in ("set_", "enter_", "select_", "upload_"):
                method_name = f"{prefix}{field_key}"
                method = getattr(self, method_name, None)
                if callable(method):
                    method(value)
                    matched = True
                    break

            if not matched and strict:
                raise AttributeError(
                    f"[{self.__class__.__name__}.fill_form] No granular atomic method found for key '{field_key}'. "
                    f"Expected one of: set_{field_key}(), select_{field_key}(), check_{field_key}(), upload_{field_key}()."
                )
        return self

    def get_form_values(self, fields: List[str]) -> Dict[str, Any]:
        """
        Reads multiple form field values at once by invoking the Page Object's
        granular Layer-2 getters (`get_<field>()` or `is_<field>()`).

        Args:
            fields (List[str]): List of field names to read (e.g. `["username", "country"]`).

        Returns:
            Dict[str, Any]: Mapping of `{field_name: current_value}`.
        """
        result: Dict[str, Any] = {}
        for field_key in fields:
            for prefix in ("get_", "is_"):
                method = getattr(self, f"{prefix}{field_key}", None)
                if callable(method):
                    result[field_key] = method()
                    break
            else:
                raise AttributeError(
                    f"[{self.__class__.__name__}.get_form_values] No getter method found for '{field_key}'. "
                    f"Expected get_{field_key}() or is_{field_key}()."
                )
        return result

    # --- Universal CRUD Helpers: Loaders & Toasts ---

    DEFAULT_LOADER_SELECTORS = (
        ".spinner-border, .loading-spinner, .loading-backdrop, .overlay-loader, "
        "[data-loading='true'], [role='progressbar'], .ant-spin, .mat-progress-spinner, "
        ".v-progress-circular, .loader, #loading, #spinner"
    )

    DEFAULT_TOAST_SELECTORS = (
        "[role='alert'], .toast, .alert-toast, .notif, .notification, "
        ".snackbar, .ant-notification, .mat-snack-bar-container, .alert-success, .alert-danger"
    )

    def wait_for_loader_to_disappear(self, locator: tuple = None, timeout: int = 15) -> Self:
        """
        Waits for a loading indicator, spinner, or backdrop overlay to disappear from the DOM.
        If no explicit locator is given, checks if this Page Object has an attribute starting
        with 'spn_' or 'ldr_'; otherwise inspects the DOM for standard Enterprise loader selectors.

        Args:
            locator (tuple, optional): Explicit (By, Value) locator for the loader.
            timeout (int): Maximum seconds to wait for disappearance. Defaults to 15s.

        Returns:
            Self: The current Page Object instance for fluent method chaining.
        """
        import time
        from selenium.webdriver.common.by import By

        # 1. Explicit locator
        if locator:
            self.element(locator).wait_disappear(timeout)
            return self

        # 2. Check if the Page Object has a declared loader attribute (e.g. spn_loader, ldr_loading)
        for attr_name in dir(self):
            if attr_name.startswith(("spn_", "ldr_", "loader_", "spinner_")):
                loader_elem = getattr(self, attr_name, None)
                if isinstance(loader_elem, UIElement):
                    loader_elem.wait_disappear(timeout)
                    return self

        # 3. Universal fallback: check common CSS loader selectors
        start_time = time.time()
        time.sleep(0.1)
        while (time.time() - start_time) < timeout:
            try:
                loaders = self.driver.find_elements(By.CSS_SELECTOR, self.DEFAULT_LOADER_SELECTORS)
                visible_loaders = [el for el in loaders if el.is_displayed()]
                if not visible_loaders:
                    return self
            except Exception:
                pass
            time.sleep(0.1)

        self.logger.warning(f"Loader did not disappear within {timeout}s or was already gone.")
        return self

    def wait_for_toast(self, locator: tuple = None, timeout: int = 10) -> UIElement:
        """
        Waits for a Toast notification or floating alert message to become visible.

        Args:
            locator (tuple, optional): Explicit locator for the toast element.
            timeout (int): Timeout in seconds to wait for toast visibility. Defaults to 10s.

        Returns:
            UIElement: The resolved toast element instance.
        """
        from selenium.webdriver.common.by import By
        target_locator = locator or (By.CSS_SELECTOR, self.DEFAULT_TOAST_SELECTORS)
        toast_el = self.element(target_locator)
        toast_el.at(timeout).wait_visible()
        return toast_el

    def get_toast_text(self, locator: tuple = None, timeout: int = 10) -> str:
        """
        Waits for a Toast notification to appear and returns its trimmed text content.

        Args:
            locator (tuple, optional): Explicit locator for the toast message text.
            timeout (int): Timeout in seconds. Defaults to 10s.

        Returns:
            str: The trimmed text of the toast notification.
        """
        toast_el = self.wait_for_toast(locator, timeout)
        return toast_el.get_trimmed_text()
