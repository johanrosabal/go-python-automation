from typing import Union, List, Dict, Self
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from core.ui.actions.selenium import (
    BaseAction,
    ClickActions,
    SendKeysActions,
    ScrollActions,
    DropdownActions,
    ElementsActions,
    CheckActions,
    RadioActions,
    TableActions,
    UploadActions,
    GetTextActions,
    ScreenshotActions,
)
import allure

class _ElementCore(BaseAction):
    """
    Core foundation for specialized UI elements and the full UIElement facade.

    This class binds a Selenium locator to a comprehensive set of actions 
    (Click, SendKeys, Select, etc.), providing a fluent and intuitive API.
    It handles automatic logging with Page Object context and dynamic 
    timeout management.
    """
    def __init__(self, driver: WebDriver, locator: tuple, page_object=None, locator_name: str = None, shadow: bool = False):
        """
        Initializes the UIElement facade.

        Args:
            driver (WebDriver): The active Selenium WebDriver instance.
            locator (tuple): The (By, Value) locator for this element.
            page_object (BasePage, optional): The parent Page Object for context.
            locator_name (str, optional): Explicit name for logging (e.g., from @find_by).
            shadow (bool, optional): Whether to enable deep Shadow DOM piercing.
        """
        super().__init__(driver)
        self.locator = locator
        self.page_object = page_object
        self._is_shadow = shadow
        
        # Metadata discovery for logging
        self.page_name = page_object.__class__.__name__ if page_object else "UnknownPage"
        self.locator_name = locator_name if locator_name else self._discover_locator_name()

        # Internal cache for lazy-initialized action components
        self._action_cache = {}

    def shadow(self: Self, is_shadow: bool = True) -> Self:
        """
        Fluently enables or disables deep Shadow DOM piercing on this element and all its bound actions.

        Returns:
            Self: The current element instance for method chaining.
        """
        self._is_shadow = is_shadow
        for action in self._action_cache.values():
            if hasattr(action, "shadow"):
                action.shadow(is_shadow)
        return self

    def _get_action(self, key: str, cls):
        """Lazily instantiates and caches an action component bound to this locator."""
        if key not in self._action_cache:
            from core.ui.actions.factory import ActionFactory
            try:
                action = ActionFactory.create(key, self.driver).set_locator(self.locator)
            except Exception:
                action = cls(self.driver).set_locator(self.locator)
            if getattr(self, "_is_shadow", False) and hasattr(action, "shadow"):
                action.shadow(True)
            self._action_cache[key] = action
        return self._action_cache[key]

    @property
    def _click(self) -> ClickActions:
        return self._get_action("click", ClickActions)

    @property
    def _send_keys(self) -> SendKeysActions:
        return self._get_action("send_keys", SendKeysActions)

    @property
    def _scroll(self) -> ScrollActions:
        return self._get_action("scroll", ScrollActions)

    @property
    def _select(self) -> DropdownActions:
        return self._get_action("select", DropdownActions)

    @property
    def _dropdown(self) -> DropdownActions:
        return self._select

    @property
    def _elements(self) -> ElementsActions:
        return self._get_action("elements", ElementsActions)

    @property
    def _check(self) -> CheckActions:
        return self._get_action("check", CheckActions)

    @property
    def _radio(self) -> RadioActions:
        return self._get_action("radio", RadioActions)

    @property
    def _table(self) -> TableActions:
        return self._get_action("table", TableActions)

    @property
    def _upload(self) -> UploadActions:
        return self._get_action("upload", UploadActions)

    @property
    def _get_text(self) -> GetTextActions:
        return self._get_action("get_text", GetTextActions)

    @property
    def _screenshot(self) -> ScreenshotActions:
        return self._get_action("screenshot", ScreenshotActions)

    def _discover_locator_name(self) -> str:
        """
        Performs a reverse lookup to find the variable name of the locator.

        Uses the parent Page Object's class dictionary to identify how 
        this locator was named in the code (e.g., 'LOGIN_BUTTON').

        Returns:
            str: The name of the locator or its value if not found.
        """
        if not self.page_object:
            return str(self.locator)
        
        for name, value in self.page_object.__class__.__dict__.items():
            if value == self.locator:
                return name
        return str(self.locator)

    def _log_action(self, action: str):
        """
        Logs a UI action with metadata context and records an event into the ActionTracer timeline.

        Args:
            action (str): Description of the action being performed.
        """
        self.logger.info(f"{self.page_name} - {action} on element: {self.locator_name} {self.locator}")
        try:
            from core.utils.action_tracer import ActionTracer
            ActionTracer.record_action(
                action=action,
                page=self.page_name,
                element=self.locator_name,
                locator=self.locator,
                duration_ms=0,
                status="PASS",
            )
        except Exception:
            pass

    @property
    def web_element(self) -> WebElement:
        """
        Resolves and returns the underlying Selenium WebElement with explicit wait and auto-healing.

        Returns:
            WebElement: The native Selenium WebElement instance.
        """
        return self.set_locator(self.locator)._find_element()

    def format(self, *args, **kwargs) -> Self:
        """
        Formats a dynamic locator template and its label with runtime parameters.

        Example:
            button_add_product = find_by(
                xpath="//div[text()='{product}']/ancestor::div[@class='inventory_item']//button",
                label="Add '{product}' Button"
            )
            self.button_add_product.format(product="Sauce Labs Backpack").click()

        Returns:
            Self: A new specialized element instance bound to the formatted locator.
        """
        by, raw_selector = self.locator
        formatted_selector = raw_selector.format(*args, **kwargs)
        formatted_name = (
            self.locator_name.format(*args, **kwargs)
            if self.locator_name and "{" in self.locator_name
            else self.locator_name
        )
        return self.__class__(
            driver=self.driver,
            locator=(by, formatted_selector),
            page_object=self.page_object,
            locator_name=formatted_name,
            shadow=self._is_shadow,
        )

    # --- Click Actions ---

class _ClickMixin(_ElementCore):

    def click(self) -> Self:
        """
        Performs a standard click on the element.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Clicking")
        self._click.at(self._get_current_timeout()).click()
        return self

    def double_click(self) -> Self:
        """
        Performs a double-click on the element.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Double clicking")
        self._click.at(self._get_current_timeout()).double_click()
        return self

    def right_click(self) -> Self:
        """
        Performs a right-click on the element.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Right clicking")
        self._click.at(self._get_current_timeout()).right_click()
        return self

    def hover(self) -> Self:
        """
        Moves the mouse pointer over the element (Hover).

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Hovering over")
        self._click.at(self._get_current_timeout()).hover()
        return self

    def js_click(self) -> Self:
        """
        Clicks the element using JavaScript.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Clicking via JS")
        self._click.at(self._get_current_timeout()).js_click()
        return self

    def click_and_hold(self) -> Self:
        """
        Clicks and holds the element.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Clicking and holding")
        self._click.at(self._get_current_timeout()).click_and_hold()
        return self

    def release_mouse(self) -> Self:
        """
        Releases the mouse button if it was being held.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Releasing mouse on")
        self._click.at(self._get_current_timeout()).release_mouse()
        return self

    def release(self) -> Self:
        """
        Alias for release_mouse().
        """
        return self.release_mouse()

    def drag_and_drop(self, target_locator: tuple) -> Self:
        """
        Drags this element and drops it onto a target locator.

        Args:
            target_locator (tuple): The (By, Value) of the destination.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Dragging to {target_locator}")
        self._click.at(self._get_current_timeout()).drag_and_drop(target_locator)
        return self

    # --- SendKeys Actions ---

class _SendKeysMixin(_ElementCore):

    def type(self, text: str, clear: bool = True) -> Self:
        """
        Enters text into the field.

        Args:
            text (str): The string to type.
            clear (bool): Whether to clear the field first. Defaults to True.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Typing '{text}' into")
        self._send_keys.at(self._get_current_timeout()).type(text, clear)
        return self

    def send_keys(self, text: str, clear: bool = True) -> Self:
        """
        Alias for type(text, clear=clear). Enters text into the input field.
        """
        return self.type(text, clear=clear)

    def type_encrypted(self, text: str, clear: bool = True) -> Self:
        """
        Enters text and masks it in logs using base64.

        Args:
            text (str): The sensitive string to type.
            clear (bool, optional): Whether to clear the field first. Defaults to True.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Typing encrypted text into")
        self._send_keys.at(self._get_current_timeout()).encrypted().type(text, clear=clear)
        return self

    def type_js(self, text: str, clear: bool = False) -> Self:
        """
        Sets element value via JavaScript (bypasses some event blockers).

        Args:
            text (str): The text to set.
            clear (bool): Whether to clear first.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Setting text '{text}' via JS in")
        self._send_keys.at(self._get_current_timeout()).type_js(text, clear=clear)
        return self

    def type_by_character(self, text: str) -> Self:
        """
        Types text character by character to simulate human typing.

        Args:
            text (str): Input text.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Typing character by character '{text}' into")
        self._send_keys.at(self._get_current_timeout()).type_by_character(text)
        return self

    def clear(self, use_js: bool = False) -> Self:
        """
        Clears the input field.

        Args:
            use_js (bool, optional): Whether to use JS events for clearing. Defaults to False.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Clearing")
        self._send_keys.at(self._get_current_timeout()).clear(use_js=use_js)
        return self

    def physical_clear(self) -> Self:
        """
        Clears the input using keyboard shortcuts (CTRL+A + BACKSPACE).

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Performing physical clear")
        self._send_keys.at(self._get_current_timeout()).physical_clear()
        return self

    def press(self, key: str) -> Self:
        """
        Sends a specific keyboard key stroke.

        Args:
            key (str): The key name (e.g., 'ENTER', 'TAB').

        Returns:
            UIElement: Self instance for method chaining.
        """
        from selenium.webdriver.common.keys import Keys
        key_val = getattr(Keys, key.upper(), None)
        if not key_val:
            raise ValueError(f"Invalid key name: {key}")
        
        self._log_action(f"Pressing {key} on")
        self._send_keys.at(self._get_current_timeout()).press(key_val, key)
        return self

    def press_enter(self) -> Self:
        """
        Presses the ENTER key.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Pressing ENTER on")
        self._send_keys.at(self._get_current_timeout()).press_enter()
        return self

    def press_tab(self) -> Self:
        """
        Presses the TAB key.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Pressing TAB on")
        self._send_keys.at(self._get_current_timeout()).press_tab()
        return self

    def press_escape(self) -> Self:
        """
        Presses the ESCAPE key.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Pressing ESCAPE on")
        self._send_keys.at(self._get_current_timeout()).press_escape()
        return self

    def press_backspace(self) -> Self:
        """
        Presses the BACKSPACE key.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Pressing BACKSPACE on")
        self._send_keys.at(self._get_current_timeout()).press_backspace()
        return self

    def press_return(self) -> Self:
        """
        Presses the RETURN key.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Pressing RETURN on")
        self._send_keys.at(self._get_current_timeout()).press_return()
        return self

    # --- Scroll Actions ---

class _ScrollMixin(_ElementCore):

    def scroll_to(self, offset: int = 0) -> Self:
        """
        Scrolls the viewport to this element.

        Args:
            offset (int): Vertical offset. Defaults to 0.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Scrolling to")
        self._scroll.at(self._get_current_timeout()).scroll_to(offset)
        return self

    def scroll_to_center(self) -> Self:
        """
        Scrolls to this element and aligns it to the center of viewport.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Scrolling to center of")
        self._scroll.at(self._get_current_timeout()).scroll_to_center()
        return self

    def scroll_to_top(self) -> Self:
        """
        Scrolls to the top of the page.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Scrolling to page top")
        self._scroll.at(self._get_current_timeout()).scroll_to_top()
        return self

    def scroll_to_bottom(self) -> Self:
        """
        Scrolls to the bottom of the page.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Scrolling to page bottom")
        self._scroll.at(self._get_current_timeout()).scroll_to_bottom()
        return self

    # --- Select Actions ---

class _SelectMixin(_ElementCore):

    def select_by_text(self, text: str) -> Self:
        """
        Selects a dropdown option by visible text.

        Args:
            text (str): Visible text of the option.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Selecting option '{text}' from")
        self._dropdown.at(self._get_current_timeout()).select_by_text(text)
        return self

    def select_by_partial_text(self, text: str) -> Self:
        """
        Selects a dropdown option containing the provided partial text.

        Args:
            text (str): Partial visible text.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Selecting partial text '{text}' from")
        self._dropdown.at(self._get_current_timeout()).select_by_partial_text(text)
        return self

    def select_by_value(self, value: str) -> Self:
        """
        Selects a dropdown option by its 'value' attribute.

        Args:
            value (str): Value attribute of the option.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Selecting value '{value}' from")
        self._dropdown.at(self._get_current_timeout()).select_by_value(value)
        return self

    def select_by_index(self, index: int) -> Self:
        """
        Selects a dropdown option by its index.

        Args:
            index (int): Zero-based index.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Selecting index {index} from")
        self._dropdown.at(self._get_current_timeout()).select_by_index(index)
        return self

    def deselect_all(self) -> Self:
        """
        Deselects all options from a multi-select dropdown.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Deselecting all from")
        self._dropdown.at(self._get_current_timeout()).deselect_all()
        return self

    def get_dropdown_options(self) -> list[str]:
        """
        Retrieves the list of all available options in the dropdown.

        Returns:
            list[str]: Collection of option texts.
        """
        self._log_action("Getting options from")
        return self._dropdown.at(self._get_current_timeout()).get_dropdown_options()

    def get_selected_text(self) -> str:
        """
        Retrieves the visible text of the currently selected option in the dropdown.

        Returns:
            str: Selected option text.
        """
        self._log_action("Getting selected option from")
        return self._dropdown.at(self._get_current_timeout()).get_selected_text()

class _CheckRadioMixin(_ElementCore):

    def check(self, state: bool = True) -> Self:
        """
        Sets the state of a checkbox.

        Args:
            state (bool): Desired state (True for checked). Defaults to True.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Checking (state={state})")
        self._check.at(self._get_current_timeout()).check(state)
        return self

    def is_checked(self) -> bool:
        """
        Returns the current selection state of a checkbox.

        Returns:
            bool: True if selected, False otherwise.
        """
        return self._check.at(self._get_current_timeout()).is_checked()

    # --- Radio Actions ---

    def select_radio(self) -> Self:
        """
        Selects a radio button.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Selecting radio")
        self._radio.at(self._get_current_timeout()).select_radio()
        return self

    def is_selected(self) -> bool:
        """
        Returns the current selection state of a radio button.

        Returns:
            bool: True if selected, False otherwise.
        """
        return self._radio.at(self._get_current_timeout()).is_selected()

    # --- Table Actions ---

class _TableMixin(_ElementCore):

    def get_cell_text(self, row: int, col: Union[int, str]) -> str:
        """
        Retrieves text from a specific cell if this element is a table.

        Args:
            row (int): 1-based row index.
            col (Union[int, str]): 1-based column index or name.

        Returns:
            str: The cell content.
        """
        self._log_action(f"Getting text from cell ({row}, {col}) of")
        return self._table.at(self._get_current_timeout()).get_cell_text(row, col)

    def get_row_count(self) -> int:
        """
        Returns the total number of rows in the table.

        Returns:
            int: The row count.
        """
        return self._table.at(self._get_current_timeout()).get_row_count()

    def get_table_headers(self) -> list[str]:
        """
        Retrieves all header texts from a table.

        Returns:
            list[str]: Headers list.
        """
        self._log_action("Getting headers of")
        return self._table.at(self._get_current_timeout()).get_table_headers()

    def click_table_header(self, text: str = None, index: int = None) -> Self:
        """
        Clicks a table header for sorting or selection.

        Args:
            text (str, optional): Header text.
            index (int, optional): 1-based index.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._table.at(self._get_current_timeout()).click_header(text, index)
        return self

    def get_table_data(self) -> list[dict]:
        """
        Parses whole table into a list of dictionaries.

        Returns:
            list[dict]: Records list.
        """
        self._log_action("Getting full data of")
        return self._table.at(self._get_current_timeout()).get_table_data()

    def table_check_all(self, column: Union[int, str] = 1) -> Self:
        """
        Checks 'select all' check in a table.

        Args:
            column (Union[int, str]): Target column.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Checking all rows in table")
        self._table.at(self._get_current_timeout()).table_check_all(column)
        return self

    def table_check_row(self, index: int, column: Union[int, str] = 1) -> Self:
        """
        Checks a specific row in a table.

        Args:
            index (int): Row index.
            column (Union[int, str]): Column index/name.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Checking row {index} in table")
        self._table.at(self._get_current_timeout()).table_check_row(index, column)
        return self

    def table_click_button(self, row: int, col: Union[int, str], text: str = None) -> Self:
        """
        Clicks a button inside a specific cell.

        Args:
            row (int): Row index.
            col (Union[int, str]): Column index/name.
            text (str): Optional button text filter.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Clicking button in table row {row}")
        self._table.at(self._get_current_timeout()).table_click_button(row, col, text)
        return self

    def table_click_link(self, row: int, col: Union[int, str], text: str = None) -> Self:
        """
        Clicks a link inside a specific cell.

        Args:
            row (int): Row index.
            col (Union[int, str]): Column index/name.
            text (str): Optional link text filter.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Clicking link in table row {row}")
        self._table.at(self._get_current_timeout()).table_click_link(row, col, text)
        return self

    def table_wait_for_rows(self, expected_count: int, timeout: int = None) -> Self:
        """
        Waits until table has exact row count.

        Args:
            expected_count (int): Row count.
            timeout (int): Custom timeout.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Waiting for table to have {expected_count} rows")
        self._table.at(self._get_current_timeout()).table_wait_for_rows(expected_count, timeout)
        return self

    def table_wait_not_empty(self, timeout: int = None) -> Self:
        """
        Waits until table is not empty.

        Args:
            timeout (int): Custom timeout.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Waiting for table not empty")
        self._table.at(self._get_current_timeout()).table_wait_not_empty(timeout)
        return self

    # --- Upload Actions ---

class _UploadMixin(_ElementCore):

    def upload_file(self, file_path: str) -> Self:
        """
        Uploads a file.

        Args:
            file_path (str): File system path.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Uploading file '{file_path}' through")
        self._upload.at(self._get_current_timeout()).upload_file(file_path)
        return self

    # --- Elements/State Actions ---

class _WaitAndStateMixin(_ElementCore):

    def wait_visible(self, timeout: int = None) -> Self:
        """
        Explicitly waits for the element to become visible on the page.

        Args:
            timeout (int, optional): Custom timeout for this wait.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Waiting for visibility of")
        self._elements.wait_visible(timeout)
        return self

    def wait_present(self) -> Self:
        """
        Waits until element is present in the DOM.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Waiting for presence of")
        self._elements.at(self._get_current_timeout()).wait_present()
        return self

    def wait_clickable(self) -> Self:
        """
        Explicitly waits for the element to be clickable (visible and enabled).

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Waiting for element to be clickable")
        self._elements.at(self._get_current_timeout()).wait_clickable()
        return self

    def wait_disappear(self, timeout: int = None) -> Self:
        """
        Explicitly waits for the element to disappear from the viewport or DOM.

        Args:
            timeout (int, optional): Custom timeout for this wait.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action("Waiting for disappearance of")
        self._elements.at(timeout if timeout else self._get_current_timeout()).wait_disappear()
        return self

    def is_enabled(self) -> bool:
        """
        Checks if the element is currently enabled.

        Returns:
            bool: True if enabled.
        """
        return self._elements.at(self._get_current_timeout()).is_enabled()

    def is_clickable(self) -> bool:
        """
        Checks if the element is currently clickable.

        Returns:
            bool: True if clickable.
        """
        return self._elements.at(self._get_current_timeout()).is_clickable()

    def is_enabled_js(self) -> bool:
        """
        Checks if the element is enabled using direct JavaScript execution.

        Returns:
            bool: True if enabled via JS.
        """
        return self._elements.at(self._get_current_timeout()).is_enabled_js()

    def get_css_value(self, property_name: str) -> str:
        """
        Retrieves a CSS property value.

        Args:
            property_name (str): The property name.

        Returns:
            str: The property value.
        """
        return self._elements.at(self._get_current_timeout()).get_css_value(property_name)

    def set_css_value(self, property_name: str, value: str) -> Self:
        """
        Sets a CSS property via JS.

        Args:
            property_name (str): Property name.
            value (str): Value to set.

        Returns:
            UIElement: Self for chaining.
        """
        self._log_action(f"Setting CSS {property_name}={value} on")
        self._elements.at(self._get_current_timeout()).set_css_value(property_name, value)
        return self

    def is_not_visible(self) -> bool:
        """
        Checks if the element is not visible or not present.

        Returns:
            bool: True if not visible.
        """
        return self._elements.at(self._get_current_timeout()).is_not_visible()

    def get_text(self) -> str:
        """
        Retrieves the element's visible text.

        Returns:
            str: The text content.
        """
        self._log_action("Getting text of")
        return self._get_text.at(self._get_current_timeout()).get_text()

    def get_trimmed_text(self) -> str:
        """
        Retrieves element's text with stripped whitespace.

        Returns:
            str: The cleaned text content.
        """
        self._log_action("Getting trimmed text of")
        return self._get_text.at(self._get_current_timeout()).get_trimmed_text()

    def get_attribute(self, attribute: str) -> str:
        """
        Retrieves the value of a specific attribute.

        Args:
            attribute (str): Attribute name.

        Returns:
            str: Attribute value.
        """
        return self._get_text.at(self._get_current_timeout()).attribute(attribute)

    def get_value(self) -> str:
        """
        Direct access to the 'value' attribute (common for inputs).

        Returns:
            str: The input value.
        """
        return self._get_text.at(self._get_current_timeout()).value()

class _TextMixin(_ElementCore):

    def wait_text_contains(self, text: str) -> Self:
        """
        Waits until the element text contains a partial string.

        Args:
            text (str): Partial text to wait for.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Waiting for text '{text}' in")
        self._elements.at(self._get_current_timeout()).wait_for_text(text)
        return self

    def contains_text(self, text: str) -> bool:
        """
        Checks if the element text currently contains a partial string.

        Args:
            text (str): Partial text to look for.

        Returns:
            bool: True if found.
        """
        return self._get_text.at(self._get_current_timeout()).contains(text)

    def wait_until_text_is(self, text: str) -> Self:
        """
        Waits until the element text matches exactly the expected string.

        Args:
            text (str): Exact text.

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Waiting until text is exactly '{text}' in")
        self._get_text.at(self._get_current_timeout()).wait_until_is(text)
        return self

    def matches_regex(self, pattern: str) -> bool:
        """
        Validates the element text against a regular expression.

        Args:
            pattern (str): The regex pattern.

        Returns:
            bool: True if matches.
        """
        return self._get_text.at(self._get_current_timeout()).matches_regex(pattern)

    def is_empty(self) -> bool:
        """
        Checks if the element has no text content.

        Returns:
            bool: True if empty.
        """
        return self._get_text.at(self._get_current_timeout()).is_empty()

    # --- HTML / Technical Retrieval ---

    def get_inner_html(self) -> str:
        """
        Retrieves the internal HTML content of the element.

        Returns:
            str: Inner HTML code.
        """
        return self._get_text.at(self._get_current_timeout()).inner_html()

    def get_outer_html(self) -> str:
        """
        Retrieves the full HTML code including the element's own tags.

        Returns:
            str: Outer HTML code.
        """
        return self._get_text.at(self._get_current_timeout()).outer_html()

    def get_text_content(self) -> str:
        """
        Captures all text content via DOM 'textContent' (includes hidden text).

        Returns:
            str: Full text content.
        """
        return self._get_text.at(self._get_current_timeout()).text_content()

    # --- Numeric Parsing ---

    def get_int(self) -> int:
        """
        Parses the element text and returns the first integer found.

        Returns:
            int: The parsed number.
        """
        return self._get_text.at(self._get_current_timeout()).get_int()

    def get_float(self) -> float:
        """
        Parses the element text and returns the first decimal found.

        Returns:
            float: The parsed float.
        """
        return self._get_text.at(self._get_current_timeout()).get_float()

    # --- Multi-Element Retrieval ---

    def all_texts(self) -> list[str]:
        """
        Retrieves a list of texts for all items matching the element's locator.

        Returns:
            list[str]: Collection of text strings.
        """
        return self._get_text.at(self._get_current_timeout()).all_texts()

    # --- Screenshot Actions ---

class _ScreenshotAndHelperMixin(_ElementCore):

    def screenshot(self, name: str = "element_screenshot") -> Self:
        """
        Captures a screenshot of this specific element.

        Args:
            name (str, optional): Descriptive name. Defaults to "element_screenshot".

        Returns:
            UIElement: Self instance for method chaining.
        """
        self._log_action(f"Taking screenshot '{name}' of")
        self._screenshot.at(self._get_current_timeout()).screenshot(name)
        return self

    def is_visible(self) -> bool:
        """
        Immediate check for element visibility.

        Returns:
            bool: True if visible.
        """
        return self._elements.at(self._get_current_timeout()).is_visible()

    # --- Helper logic ---

    def _get_current_timeout(self) -> int:
        """
        Internal helper to extract the active fluent timeout for delegation.

        Returns:
            int: Current timeout in seconds.
        """
        return int(self._current_wait._timeout)


class InputElement(_SendKeysMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only input/typing, reading, and state actions."""
    pass


class ButtonElement(_ClickMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only click, hover, and state actions."""
    pass


class TextElement(_TextMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only text reading, assertion, and wait actions."""
    pass


class DropdownElement(_SelectMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only dropdown selection and state actions."""
    pass


class CheckboxElement(_CheckRadioMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only checkbox/radio and state actions."""
    pass


class TableElement(_TableMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing only table inspection, cell interaction, and state actions."""
    pass


class UploadElement(_UploadMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element exposing file upload and state actions."""
    pass


class ContainerElement(_TextMixin, _ClickMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element for modals, dialogs, cards, panels, loaders, and layout sections."""
    pass


class MediaElement(_ClickMixin, _WaitAndStateMixin, _ScrollMixin, _ScreenshotAndHelperMixin, _ElementCore):
    """Specialized UI element for images, icons, avatars, banners, videos, and canvas elements."""
    pass


class UIElement(
    InputElement,
    ButtonElement,
    TextElement,
    DropdownElement,
    CheckboxElement,
    TableElement,
    UploadElement,
    ContainerElement,
    MediaElement,
):
    """
    Primary interface for interacting with UI elements (Facade Pattern).

    Exposes all available UI actions when no specific element type restriction applies.
    """
    pass

