# Page Object Creation Standards

To ensure consistency, readability, and high maintainability across the enterprise automation framework, all Page Objects and UI Components must follow these strict rules:

## 1. Declarative Locators with `find_by` and Semantic Prefixes
All static locators must be declared at the class level using `find_by` (from `core.ui.common.find_by`) and must start with a recognized semantic prefix so the framework automatically resolves the specialized element type (`InputElement`, `ButtonElement`, `TextElement`, etc.) and validates naming conventions:

| Category | Element Type | Allowed Prefixes |
| :--- | :--- | :--- |
| **Inputs / Fields** | `InputElement` | `input_`, `inp_`, `in_`, `field_`, `textarea_`, `search_`, `date_`, `datepicker_` |
| **Buttons / Links / Icons** | `ButtonElement` | `btn_`, `button_`, `lnk_`, `link_`, `ico_`, `icon_`, `svg_`, `tab_`, `mnu_`, `menu_`, `nav_`, `itm_`, `item_`, `sld_`, `slider_` |
| **Labels / Text / Alerts** | `TextElement` | `lbl_`, `label_`, `txt_`, `text_`, `hdr_`, `header_`, `ttl_`, `title_`, `msg_`, `message_`, `alrt_`, `alert_`, `toast_`, `err_`, `error_`, `bdg_`, `badge_`, `status_`, `tlt_`, `tooltip_`, `lst_`, `list_` |
| **Dropdowns / Selects** | `DropdownElement` | `ddl_`, `select_`, `sel_`, `cmb_`, `combo_`, `dropdown_`, `multiselect_` |
| **Checkboxes / Radios / Toggles** | `CheckboxElement` | `chk_`, `check_`, `checkbox_`, `rdo_`, `radio_`, `tgl_`, `toggle_`, `swt_`, `switch_` |
| **Tables / Grids** | `TableElement` | `tbl_`, `table_`, `grd_`, `grid_` |
| **File Uploads** | `UploadElement` | `upl_`, `upload_`, `file_` |
| **Modals / Cards / Containers** | `ContainerElement` | `mdl_`, `modal_`, `dlg_`, `dialog_`, `popup_`, `drawer_`, `crd_`, `card_`, `pnl_`, `panel_`, `sec_`, `section_`, `cnt_`, `container_`, `frm_`, `form_`, `ifrm_`, `iframe_`, `ldr_`, `loader_`, `spn_`, `spinner_` |
| **Media / Graphics** | `MediaElement` | `img_`, `image_`, `pic_`, `avatar_`, `logo_`, `banner_`, `vid_`, `video_`, `cnv_`, `canvas_` |

*   **Optional `label` Attribute:** Pass `label="Human Readable Name"` in `find_by(...)` (especially when using complex XPath/CSS selectors) so logs display a clear business name. If omitted, the framework auto-humanizes the variable name (e.g., `input_first_name` -> `"First Name Input"`).
*   **Page Readiness Contract (`PAGE_PATH` + `anchor=True`):** Declare `PAGE_PATH = "/route"` (optional) and mark 1-2 key locators with `anchor=True` so `page.open()`, `page.is_loaded()`, and `page.wait_until_loaded()` work uniformly across all Page Objects.
*   **Dynamic Parameterized Locators (`.format()`):** Keep dynamic locators in Layer 1 using `{placeholder}` syntax and format them inside Layer-2 methods via `self.button_item.format(name=val).click()`.
*   **Fallback Behavior:** If a locator variable does not start with a standard prefix, a `[NAMING CONVENTION]` warning is logged and the framework falls back to exposing all `UIElement` methods.

## 2. Granular Atomic Methods (Layer 2: Setters, Getters & Clicks)
Every form field or interactive locator defined in a Page Object **MUST** have its own dedicated atomic methods:

*   **Setter / Selection Methods (`-> Self`):** `set_[field_name](val)`, `select_[field_name](val)`, `check_[field_name]()`, `uncheck_[field_name]()`, `upload_[field_name](path)`.
*   **Getter / State Methods:** `get_[field_name]() -> str`, `is_[field_name]() -> bool`.
*   **Action Methods (`-> Self`):** `click_[element_name]()`.

## 3. Method Chaining & `Self` Typing (Fluent Interface)
All interaction and setter methods **MUST** return `self` annotated with `-> Self` so the IDE preserves subclass autocomplete across fluent chains.

## 4. Reusable UI Components (`BaseComponent` & `component(...)`)
Shared UI sections present across multiple pages (such as sidebars, headers, navigation bars, or global modals) **MUST** inherit from `BaseComponent` (`core.ui.common.base_component`) and be attached declaratively via `sidebar = component(SidebarComponent)`.

## 5. Composite Methods & Smart Form Orchestration (Layer 3)
High-level interactions (like `login`, `fill_checkout_form`, `complete_checkout`) **MUST** be built by reusing the Layer-2 granular methods or by calling `self.fill_form(data)` (which automatically maps dictionary keys to `set_<key>`, `select_<key>`, `check_<key>`, `upload_<key>`).

## Example Pattern (3-Layer Standard)

```python
from typing import Self, Dict, Any
from core.ui.common.base_page import BasePage
from core.ui.common.base_component import component
from core.ui.common.find_by import find_by
from applications.web.demo.components.sidebar_component import SidebarComponent
import allure


class ExamplePage(BasePage):
    PAGE_PATH = "/search"

    # LAYER 1: Declarative Locators & Components
    input_search = find_by(id="search", label="Search Term Input", anchor=True)
    button_search = find_by(xpath="//button[@type='submit']", label="Search Submit Button")
    button_result_item = find_by(xpath="//div[text()='{item}']/button", label="Select '{item}' Button")
    text_error_message = find_by(css="[data-test='error']", label="Search Error Message")

    sidebar = component(SidebarComponent)

    # LAYER 2: Granular Atomic Methods (Setters, Getters & Clicks)
    @allure.step("Setting search term: {term}")
    def set_search_term(self, term: str) -> Self:
        self.input_search.send_keys(term)
        return self

    def get_search_term(self) -> str:
        return self.input_search.get_value()

    @allure.step("Clicking search button")
    def click_search(self) -> Self:
        self.button_search.click()
        return self

    def click_result_item(self, item_name: str) -> Self:
        self.button_result_item.format(item=item_name).click()
        return self

    def get_error_message(self) -> str:
        return self.text_error_message.wait_visible().get_text()

    # LAYER 3: Composite Business / Form Methods
    def perform_search(self, term: str) -> Self:
        return self.set_search_term(term).click_search()

    def perform_search_from_data(self, data: Dict[str, Any]) -> Self:
        return self.fill_form(data).click_search()
```
