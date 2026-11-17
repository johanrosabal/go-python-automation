from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from core.utils.logger_config import setup_logger
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import logging
import allure
from typing import TypeVar

T = TypeVar('T', bound='BaseAction')

class BaseAction:
    """
    Foundational base class for all UI action components.

    Provides essential utilities inherited by specialized action classes, 
    including direct access to WebDriver, support for fluent timeout management 
    via explicit waits, and a centralized exception handling mechanism.
    """
    def __init__(self, driver: WebDriver):
        """
        Initializes the BaseAction component.

        Args:
            driver (WebDriver): The active Selenium WebDriver instance.
        """
        self.driver = driver
        self.default_timeout = 10
        self._wait = WebDriverWait(self.driver, self.default_timeout)
        self._current_wait = self._wait
        self._locator = None
        self._element = None
        self._is_shadow = False
        self.logger = setup_logger(self.__class__.__name__)

    def at(self: T, timeout: int) -> T:
        """
        Fluently sets a temporary timeout for the immediate next operation.

        This method allows overriding the default timeout for a specific wait 
        without affecting subsequent actions.

        Args:
            timeout (int): The temporary timeout duration in seconds.

        Returns:
            BaseAction: The current instance for method chaining (fluent API).
        """
        self.logger.debug(f"Setting temporary timeout to {timeout}s")
        self._current_wait = WebDriverWait(self.driver, timeout)
        return self

    def shadow(self: T, is_shadow: bool = True) -> T:
        """
        Fluently enables or disables deep Shadow DOM piercing for this action/element.

        Args:
            is_shadow (bool): If True, elements will be searched across open Shadow Roots.

        Returns:
            BaseAction: The current instance for method chaining.
        """
        self._is_shadow = is_shadow
        return self

    def set_locator(self: T, locator: tuple) -> T:
        """
        Sets the locator and clears any previously found element.

        Args:
            locator (tuple): The (By, Value) locator.

        Returns:
            BaseAction: The current instance for method chaining.
        """
        self._locator = locator
        self._element = None
        return self

    def _find_in_shadow_dom(self):
        """
        Deeply pierces open Shadow DOM roots recursively across the entire document tree.
        Supports CSS selectors, IDs, names, tags, classes, and text content matching.
        """
        if not self._locator:
            return None

        by, val = self._locator
        by_str = str(by).lower()
        val_str = str(val)

        # Map locator to JS strategy & parameter
        strategy = "css"
        param = val_str

        if "id" in by_str:
            strategy = "id"
            param = val_str
        elif "name" in by_str:
            strategy = "name"
            param = val_str
        elif "class" in by_str:
            strategy = "css"
            param = f".{val_str}"
        elif "tag" in by_str:
            strategy = "css"
            param = val_str
        elif "css" in by_str:
            strategy = "css"
            param = val_str
        elif "xpath" in by_str:
            import re
            if "text()" in val_str or "normalize-space()" in val_str:
                if "contains(" in val_str:
                    strategy = "text_contains"
                    m = re.search(r"contains\(\s*(?:text\(\)|normalize-space\(\))\s*,\s*['\"]([^'\"]+)['\"]", val_str)
                    param = m.group(1) if m else val_str
                else:
                    strategy = "text"
                    m = re.search(r"['\"]([^'\"]+)['\"]", val_str)
                    param = m.group(1) if m else val_str
            else:
                strategy = "xpath_fallback"
                param = val_str

        shadow_script = """
        function findDeep(strategy, val, root) {
            root = root || document;

            function matches(el) {
                if (!el || el.nodeType !== 1) return false;
                try {
                    if (strategy === 'css') {
                        return el.matches && el.matches(val);
                    } else if (strategy === 'id') {
                        return el.id === val || el.getAttribute('id') === val;
                    } else if (strategy === 'name') {
                        return el.getAttribute && el.getAttribute('name') === val;
                    } else if (strategy === 'text') {
                        return (el.textContent || '').trim() === val;
                    } else if (strategy === 'text_contains') {
                        return (el.textContent || '').includes(val);
                    }
                } catch(e) {}
                return false;
            }

            // Quick CSS querySelector if applicable
            if (strategy === 'css' || strategy === 'id' || strategy === 'name') {
                var query = strategy === 'css' ? val : (strategy === 'id' ? '#' + CSS.escape(val) : '[name="' + CSS.escape(val) + '"]');
                try {
                    var fastMatch = root.querySelector(query);
                    if (fastMatch) return fastMatch;
                } catch(e) {}
            }

            // Recursive traversal through light DOM and all open Shadow DOMs
            var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            var node = walker.nextNode();
            while (node) {
                if (matches(node)) return node;
                if (node.shadowRoot) {
                    var inShadow = findDeep(strategy, val, node.shadowRoot);
                    if (inShadow) return inShadow;
                }
                node = walker.nextNode();
            }
            return null;
        }
        return findDeep(arguments[0], arguments[1]);
        """
        try:
            return self.driver.execute_script(shadow_script, strategy, param)
        except Exception as e:
            self.logger.debug(f"Shadow DOM query error: {e}")
            return None

    def _find_element(self, condition=None) -> "BaseAction":
        """
        Internal helper to find and cache the element using the set locator.
        Features Transparent Deep Shadow DOM Piercing and Auto-healing logic.
        
        Args:
            condition: Optional Selenium Expected Condition. 
                       Defaults to presence_of_element_located.
        """
        if not self._locator:
            raise ValueError("Locator not set. Call 'set_locator()' first.")
        
        # 1. Direct Shadow DOM path if explicitly marked
        if self._is_shadow:
            import time
            start = time.time()
            timeout = getattr(self, "default_timeout", 10)
            while (time.time() - start) < timeout:
                element = self._find_in_shadow_dom()
                if element:
                    self._element = element
                    return self._element
                time.sleep(0.2)
            raise NoSuchElementException(f"Shadow DOM element {self._locator} not found within {timeout}s.")

        from selenium.webdriver.support import expected_conditions as EC
        cond = condition if condition else EC.presence_of_element_located(self._locator)
        
        try:
            # 2. Primary Standard Attempt
            self._element = self._get_wait().until(cond)
            return self._element
        except (TimeoutException, NoSuchElementException) as exc:
            # 3. Transparent Shadow DOM Piercing (Automatic Fallback)
            shadow_el = self._find_in_shadow_dom()
            if shadow_el:
                self.logger.info(f"[SHADOW-DOM] Found element {self._locator} inside Shadow Root (Transparent Piercing).")
                self._element = shadow_el
                return self._element

            # 4. Auto-healing Attempt
            self.logger.warning(f"[AUTO-HEALING] Primary locator {self._locator} failed. Attempting recovery...")
            healed_element = self._attempt_healing()
            if healed_element:
                self.logger.warning(f"[AUTO-HEALING] Successfully recovered element using fuzzy matching!")
                self._element = healed_element
                return self._element
            raise exc

    def _attempt_healing(self):
        """
        Tries to find the element using alternative strategies.
        Phase 1: Fuzzy matching by text or partial attributes.
        """
        by, value = self._locator
        
        # Strategy A: If it's an ID or Name, try 'contains'
        if by in ["id", "name"]:
            selectors = [
                 f"//*[contains(@{by}, '{value}')]",
                 f"//*[@*[contains(., '{value}')]]"
            ]
            for xpath in selectors:
                elements = self.driver.find_elements("xpath", xpath)
                if elements: return elements[0]

        # Strategy B: If it's XPath/CSS, try to find by text if value contains quotes
        # Example: //button[text()='Login'] -> //button[contains(text(), 'Login')]
        if "text()" in value:
             clean_text = value.split("'")[1] if "'" in value else value.split('"')[1] if '"' in value else None
             if clean_text:
                 elements = self.driver.find_elements("xpath", f"//*[contains(text(), '{clean_text}')]")
                 if elements: return elements[0]
        
        return None

    def _get_wait(self) -> WebDriverWait:
        """
        Retrieves the currently active wait object and resets it to default.

        This is an internal helper used by subclasses to ensure that 
        temporary timeouts are only applied once.

        Returns:
            WebDriverWait: The Selenium wait instance to be used for the next action.
        """
        wait = self._current_wait
        self._current_wait = self._wait  # Reset to default
        return wait

    def _handle_exception(self, exception: Exception, method_name: str, locator: tuple = None):
        """
        Centralized logic for exception categorization, logging, and reporting.

        Intercepts common Selenium exceptions to provide descriptive log messages 
        before re-raising them to the test layer.

        Args:
            exception (Exception): The raw exception object.
            method_name (str): The name of the action method where the error originated.
            locator (tuple, optional): The element locator involved in the failure.
                If not provided, uses the internal self._locator.

        Raises:
            Exception: Re-raises the original exception after logging.
        """
        target_locator = locator if locator else self._locator
        msg = f"Error in '{method_name}'"
        if target_locator:
            msg += f" for element {target_locator}"
        
        if isinstance(exception, TimeoutException):
            self.logger.error(f"{msg}: Timeout reached.")
        elif isinstance(exception, NoSuchElementException):
            self.logger.error(f"{msg}: No such element found.")
        elif isinstance(exception, WebDriverException):
            self.logger.error(f"{msg}: WebDriver error -> {getattr(exception, 'msg', str(exception))}")
        else:
            self.logger.error(f"{msg}: Unexpected error -> {str(exception)}")
        
        raise exception

    def pause(self: T, seconds: int = 1) -> T:
        """
        Pauses execution for a specified duration.

        Args:
            seconds (int): Duration in seconds. Defaults to 1.

        Returns:
            BaseAction: The current instance for method chaining.
        """
        import time
        self.logger.info(f"Pausing for {seconds} second(s)...")
        time.sleep(seconds)
        return self
