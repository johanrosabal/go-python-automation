---
name: create-page-object
description: >-
  Creates or updates a Page Object Model (POM) class and reusable UI Components following the framework's strict 3-Layer Granular Standard (find_by with semantic prefixes, PAGE_PATH, anchor=True, atomic set/get/click methods, composite methods, and App Orchestrator registration). Use this skill whenever the user asks to create, model, map, or update a Page Object or UI Component, optionally inspecting a live URL via the Selenium MCP.
---

# Skill: Create Page Object (3-Layer Granular Standard & Official Framework Method Catalog)

When creating or updating a Page Object (`applications/web/<app>/pages/<name>_page.py`) or Reusable Component (`applications/web/<app>/components/<name>_component.py`), you **MUST** strictly obey the **3-Layer Architecture** and **ONLY** invoke methods from the **Official Framework Method Catalog** below. **NEVER invent or hallucinate methods outside this catalog.**

---

## 0. Official Framework Method Catalog (Strict Whitelist)

### A. Common Methods Available on ALL `find_by` Elements
Every locator declared with `find_by(...)` inherits from `_ElementCore`, `_WaitAndStateMixin`, `_ScrollMixin`, and `_ScreenshotAndHelperMixin`:
- **Dynamic Formatting & Timeout**:
  - `.format(*args, **kwargs) -> Self` (Replaces `{placeholder}` in dynamic selector and label)
  - `.at(timeout: int) -> Self` (Overrides fluent timeout in seconds for the chained action)
- **Waits (Fluent `-> Self`)**:
  - `.wait_visible(timeout: int = None) -> Self`
  - `.wait_present() -> Self`
  - `.wait_clickable() -> Self`
  - `.wait_disappear(timeout: int = None) -> Self`
- **State & Attribute Checks**:
  - `.is_visible() -> bool`
  - `.is_not_visible() -> bool`
  - `.is_enabled() -> bool`
  - `.is_enabled_js() -> bool`
  - `.is_clickable() -> bool`
  - `.get_text() -> str`
  - `.get_trimmed_text() -> str`
  - `.get_value() -> str` (Returns the `value` attribute)
  - `.get_attribute(attribute: str) -> str`
  - `.get_css_value(property_name: str) -> str`
  - `.set_css_value(property_name: str, value: str) -> Self`
- **Scroll & Screenshot (`-> Self`)**:
  - `.scroll_to(offset: int = 0) -> Self`
  - `.scroll_to_center() -> Self`
  - `.scroll_to_top() -> Self`
  - `.scroll_to_bottom() -> Self`
  - `.screenshot(name: str = "element_screenshot") -> Self`

---

### B. Specialized Methods by Semantic Prefix (`find_by` Auto-Typing)
The variable name prefix of `find_by(...)` determines which specialized class is returned and **restricts** which methods can be called:

#### 1. `InputElement` — Prefixes: `input_`, `inp_`, `field_`, `textarea_`, `search_`, `date_`
- `.type(text: str, clear: bool = True) -> Self` (or alias `.send_keys(text: str, clear: bool = True) -> Self`)
- `.type_encrypted(text: str, clear: bool = True) -> Self` (Masks sensitive text in Base64 in logs)
- `.type_js(text: str, clear: bool = False) -> Self`
- `.type_by_character(text: str) -> Self`
- `.clear(use_js: bool = False) -> Self`
- `.physical_clear() -> Self` (`CTRL+A` + `BACKSPACE`)
- `.press(key: str) -> Self` (e.g., `'ENTER'`, `'TAB'`)
- `.press_enter() -> Self`, `.press_tab() -> Self`, `.press_escape() -> Self`, `.press_backspace() -> Self`, `.press_return() -> Self`
- `.get_value() -> str` (Used in Layer 2 `get_<field>()` getter methods)

#### 2. `ButtonElement` — Prefixes: `btn_`, `button_`, `lnk_`, `link_`, `ico_`, `icon_`, `tab_`, `menu_`, `nav_`
- `.click() -> Self`
- `.double_click() -> Self`
- `.right_click() -> Self`
- `.hover() -> Self`
- `.js_click() -> Self`
- `.click_and_hold() -> Self`
- `.release_mouse() -> Self` (or `.release() -> Self`)
- `.drag_and_drop(target_locator: tuple) -> Self`

#### 3. `TextElement` — Prefixes: `lbl_`, `label_`, `txt_`, `text_`, `hdr_`, `title_`, `msg_`, `err_`, `error_`, `badge_`, `alert_`, `toast_`
- `.get_text() -> str`, `.get_trimmed_text() -> str`, `.get_text_content() -> str`
- `.all_texts() -> list[str]` (Returns texts of all elements matching the locator)
- `.get_int() -> int`, `.get_float() -> float`
- `.contains_text(text: str) -> bool`, `.matches_regex(pattern: str) -> bool`, `.is_empty() -> bool`
- `.wait_text_contains(text: str) -> Self`, `.wait_until_text_is(text: str) -> Self`
- `.get_inner_html() -> str`, `.get_outer_html() -> str`

#### 4. `DropdownElement` — Prefixes: `ddl_`, `select_`, `cmb_`, `combo_`, `dropdown_`
- `.select_by_text(text: str) -> Self`
- `.select_by_partial_text(text: str) -> Self`
- `.select_by_value(value: str) -> Self`
- `.select_by_index(index: int) -> Self`
- `.deselect_all() -> Self`
- `.get_selected_text() -> str` (Used in Layer 2 `get_<field>()` getter methods)
- `.get_dropdown_options() -> list[str]`

#### 5. `CheckboxElement` — Prefixes: `chk_`, `checkbox_`, `rdo_`, `radio_`, `tgl_`, `toggle_`, `swt_`, `switch_`
- `.check(state: bool = True) -> Self` (Use `.check(True)` to check, `.check(False)` to uncheck)
- `.is_checked() -> bool` (Used in Layer 2 `is_<field>_checked()` getter methods)
- `.select_radio() -> Self`
- `.is_selected() -> bool`

#### 6. `TableElement` — Prefixes: `tbl_`, `table_`, `grd_`, `grid_`
- `.get_cell_text(row: int, col: int | str) -> str`
- `.get_row_count() -> int`
- `.get_table_headers() -> list[str]`
- `.get_table_data() -> list[dict]`
- `.click_table_header(text: str = None, index: int = None) -> Self`
- `.table_check_all(column: int | str = 1) -> Self`
- `.table_check_row(index: int, column: int | str = 1) -> Self`
- `.table_click_button(row: int, col: int | str, text: str = None) -> Self`
- `.table_click_link(row: int, col: int | str, text: str = None) -> Self`
- `.table_wait_for_rows(expected_count: int, timeout: int = None) -> Self`
- `.table_wait_not_empty(timeout: int = None) -> Self`

#### 7. `UploadElement` — Prefixes: `upl_`, `upload_`, `file_`
- `.upload_file(file_path: str) -> Self`

#### 8. `ContainerElement` — Prefixes: `mdl_`, `modal_`, `dlg_`, `dialog_`, `crd_`, `card_`, `pnl_`, `panel_`, `sec_`, `cnt_`, `frm_`, `ldr_`, `spn_`
- Combines all `TextElement` methods + `ButtonElement` methods + `_WaitAndStateMixin` (ideal for modals, cards, panels, and spinners like `.wait_disappear()`).

#### 9. `MediaElement` — Prefixes: `img_`, `image_`, `avatar_`, `logo_`, `vid_`, `cnv_`
- Combines all `ButtonElement` methods + `_WaitAndStateMixin`.

---

### C. Official `BasePage` Inherited Methods (`self.<method>`)
Inside any Page Object (`class MyPage(BasePage)`), these built-in methods and properties are available on `self`:
- **Navigation & Readiness Contract**:
  - `PAGE_PATH: str = "/..."` (Class attribute defining relative route)
  - `self.open(url: str = None) -> Self` (Opens `base_url + PAGE_PATH` or custom URL)
  - `self.open_relative(path: str) -> Self`
  - `self.is_loaded() -> bool` (Validates `PAGE_PATH` in URL + visibility of all `anchor=True` elements)
  - `self.wait_until_loaded(timeout: int = None) -> Self` (Waits for `PAGE_PATH` + all `anchor=True` elements)
- **Smart Form Orchestration (Layer 3 -> Layer 2)**:
  - `self.fill_form(data: Dict[str, Any], strict: bool = False) -> Self` (Automatically invokes `set_<key>`, `select_<key>`, `check_<key>`/`uncheck_<key>`, `upload_<key>` for every key in `data` or `tests.data`)
  - `self.get_form_values(fields: List[str]) -> Dict[str, Any]` (Invokes `get_<key>` or `is_<key>` for each field name and returns a dict)
- **Universal CRUD Synchronization & Toasts**:
  - `self.wait_for_loader_to_disappear(locator: tuple = None, timeout: int = 15) -> Self` (Mandatory in Layer 3 CRUD methods before returning)
  - `self.wait_for_toast(locator: tuple = None, timeout: int = 10) -> UIElement`
  - `self.get_toast_text(locator: tuple = None, timeout: int = 10) -> str`
- **Browser & Context Managers**:
  - `self.navigation` (`NavigationActions`: `.refresh()`, `.back()`, `.forward()`, `.wait_url_contains(text)`, `.get_current_url()`, `.get_title()`)
  - `self.window` (`SwitchWindowsActions`: `.switch_to_new_window()`, `.switch_to_window_by_title(title)`, `.close_current_window()`, `.set_zoom_level(pct)`)
  - `self.frame` (`FrameActions`: `.switch_to_frame(locator)`, `.switch_to_default_content()`)
  - `self.alert` (`AlertActions`: `.accept()`, `.dismiss()`, `.get_text()`, `.send_keys(text)`)
  - `self.screenshot` (`ScreenshotActions`: `.full_page(name)`)
- **Quality & Non-Functional Audits**:
  - `self.assert_visual_match(test_name: str, threshold: float = 0.01) -> Self`
  - `self.assert_no_accessibility_violations(impact_level: str = "critical") -> Self`
  - `self.capture_performance_metrics() -> dict`

---

## Step 1: Inspect the Target Page (If a URL or Live Page is Involved)
1. If the user provides a URL or asks to inspect a web page, use the **`selenium` MCP tools** (`start_browser`, `navigate`, `execute_script`, `interact`, `get_element_attribute`) to inspect the real DOM elements (`id`, `name`, `data-test`, `css`, or `xpath`) before writing code.
2. Identify:
   - The relative URL path of the page (`PAGE_PATH = "/..."`).
   - The 1 or 2 key elements that confirm the page finished loading (`anchor=True`).
   - Whether any section is a shared widget across pages (sidebar, header, navbar, modal) that belongs in `applications/web/<app>/components/<name>_component.py` inheriting from `BaseComponent`.

## Step 2: Build the Page Object Using the 3-Layer Standard
Create `applications/web/<app>/pages/<name>_page.py` inheriting from `BasePage`. **Never mix layers or skip Layer 2:**

```python
from typing import Self, Dict, Any
from core.ui.common.base_page import BasePage
from core.ui.common.base_component import component
from core.ui.common.find_by import find_by
import allure


class CheckoutPage(BasePage):
    PAGE_PATH = "/checkout-step-one.html"

    # =========================================================================
    # LAYER 1: Declarative Locators (Prefix + Label + Anchor) & Components
    # =========================================================================
    lbl_title = find_by(class_name="title", label="Checkout Title", anchor=True)
    input_first_name = find_by(id="first-name", label="First Name Input")
    input_last_name = find_by(id="last-name", label="Last Name Input")
    input_postal_code = find_by(id="postal-code", label="Postal Code Input")
    ddl_country = find_by(id="country", label="Country Dropdown")
    chk_terms = find_by(id="terms", label="Accept Terms Checkbox")
    button_continue = find_by(id="continue", label="Continue Button")
    text_error = find_by(css="[data-test='error']", label="Checkout Error Banner")

    # Dynamic locator template (if needed):
    # button_dynamic_item = find_by(xpath="//div[text()='{item}']/button", label="Item '{item}' Button")

    # Reusable component (if needed):
    # sidebar = component(SidebarComponent)

    # =========================================================================
    # LAYER 2: Granular Atomic Methods (Setters, Getters, Selects, Checks, Clicks)
    # =========================================================================
    @allure.step("Setting first name: {first_name}")
    def set_first_name(self, first_name: str) -> Self:
        self.input_first_name.type(first_name)
        return self

    def get_first_name(self) -> str:
        return self.input_first_name.get_value()

    @allure.step("Setting last name: {last_name}")
    def set_last_name(self, last_name: str) -> Self:
        self.input_last_name.type(last_name)
        return self

    def get_last_name(self) -> str:
        return self.input_last_name.get_value()

    @allure.step("Setting postal code: {postal_code}")
    def set_postal_code(self, postal_code: str) -> Self:
        self.input_postal_code.type(postal_code)
        return self

    def get_postal_code(self) -> str:
        return self.input_postal_code.get_value()

    @allure.step("Selecting country: {country}")
    def select_country(self, country: str) -> Self:
        self.ddl_country.select_by_text(country)
        return self

    def get_country(self) -> str:
        return self.ddl_country.get_selected_text()

    @allure.step("Checking accept terms")
    def check_terms(self) -> Self:
        self.chk_terms.check(True)
        return self

    @allure.step("Unchecking accept terms")
    def uncheck_terms(self) -> Self:
        self.chk_terms.check(False)
        return self

    def is_terms_checked(self) -> bool:
        return self.chk_terms.is_checked()

    @allure.step("Clicking continue button")
    def click_continue(self) -> Self:
        self.button_continue.click()
        return self

    def get_error_message(self) -> str:
        return self.text_error.wait_visible().get_text()

    # =========================================================================
    # LAYER 3: Composite Business / Form Methods (Orchestrate Layer 2 ONLY)
    # =========================================================================
    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str) -> Self:
        return (
            self.set_first_name(first_name)
            .set_last_name(last_name)
            .set_postal_code(postal_code)
            .click_continue()
        )

    def submit_checkout_with_data(self, data: Dict[str, Any]) -> Self:
        return self.fill_form(data).click_continue()
```

## Step 3: Register the Page Object in the App Orchestrator
Open `applications/web/<app>/app/<app>_app.py` (e.g., `applications/web/demo/app/demo_app.py`), import the new Page Object class, and expose it as a `@property`:

```python
@property
def checkout_page(self) -> CheckoutPage:
    if not hasattr(self, "_checkout_page") or self._checkout_page is None:
        self._checkout_page = CheckoutPage(self.driver)
    return self._checkout_page
```

## Step 4: Strict Checklist Verification
- [ ] Every locator in Layer 1 uses `find_by(...)` and starts with a valid prefix (`input_`, `btn_`/`button_`, `lbl_`/`text_`, `ddl_`, `chk_`, `tbl_`, `upl_`, `mdl_`, `img_`).
- [ ] Key page-load elements have `anchor=True` and `PAGE_PATH` is defined if the page has a known URL path.
- [ ] Every interactive element in Layer 1 has its corresponding Layer 2 atomic methods (`set_*`/`get_*`, `select_*`/`get_*`, `check_*`/`uncheck_*`/`is_*`, `click_*`).
- [ ] Only methods from **Section 0 (Official Framework Method Catalog)** are called on `find_by` elements and `self`.
- [ ] Layer 3 composite methods **never** access Layer 1 `find_by` attributes directly; they only chain Layer 2 methods or call `self.fill_form(data)`.
- [ ] The Page Object is registered as a `@property` in `<app>_app.py`.
