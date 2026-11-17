from selenium.webdriver.common.by import By
from core.ui.actions.ui_element import (
    UIElement,
    InputElement,
    ButtonElement,
    TextElement,
    DropdownElement,
    CheckboxElement,
    TableElement,
    UploadElement,
    ContainerElement,
    MediaElement,
)


_BY_MAP = {
    "id": By.ID,
    "css": By.CSS_SELECTOR,
    "css_selector": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "name": By.NAME,
    "class_name": By.CLASS_NAME,
    "tag": By.TAG_NAME,
    "tag_name": By.TAG_NAME,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
}

_INPUT_PREFIXES = (
    "input_", "inp_", "in_", "field_", "textarea_", "search_", "date_", "datepicker_",
)
_BUTTON_PREFIXES = (
    "btn_", "button_", "lnk_", "link_", "ico_", "icon_", "svg_",
    "tab_", "mnu_", "menu_", "nav_", "page_", "chip_", "tag_",
    "itm_", "item_", "sld_", "slider_", "range_",
)
_TEXT_PREFIXES = (
    "lbl_", "label_", "txt_", "text_", "span_", "p_",
    "hdr_", "header_", "ttl_", "title_", "subtitle_",
    "msg_", "message_", "alrt_", "alert_", "toast_", "notif_",
    "err_", "error_", "warn_", "bdg_", "badge_", "counter_",
    "pill_", "status_", "tlt_", "tooltip_", "popover_",
    "lst_", "list_", "row_", "col_", "cell_",
)
_DROPDOWN_PREFIXES = (
    "ddl_", "select_", "sel_", "cmb_", "combo_", "dropdown_", "multiselect_",
)
_CHECKBOX_PREFIXES = (
    "chk_", "check_", "checkbox_", "rdo_", "radio_",
    "tgl_", "toggle_", "swt_", "switch_",
)
_TABLE_PREFIXES = (
    "tbl_", "table_", "grd_", "grid_",
)
_UPLOAD_PREFIXES = (
    "upl_", "upload_", "file_",
)
_CONTAINER_PREFIXES = (
    "mdl_", "modal_", "dlg_", "dialog_", "popup_", "drawer_",
    "crd_", "card_", "pnl_", "panel_", "acc_", "accordion_",
    "sec_", "section_", "div_", "box_", "cnt_", "container_",
    "wrp_", "wrapper_", "ftr_", "footer_", "sidebar_", "frm_", "form_",
    "ifrm_", "iframe_", "frame_", "prg_", "progress_",
    "ldr_", "loader_", "spn_", "spinner_", "skeleton_",
)
_MEDIA_PREFIXES = (
    "img_", "image_", "pic_", "avatar_", "logo_", "banner_",
    "vid_", "video_", "aud_", "audio_", "cnv_", "canvas_",
)

_PREFIX_RULES = [
    (_INPUT_PREFIXES, InputElement),
    (_BUTTON_PREFIXES, ButtonElement),
    (_TEXT_PREFIXES, TextElement),
    (_DROPDOWN_PREFIXES, DropdownElement),
    (_CHECKBOX_PREFIXES, CheckboxElement),
    (_TABLE_PREFIXES, TableElement),
    (_UPLOAD_PREFIXES, UploadElement),
    (_CONTAINER_PREFIXES, ContainerElement),
    (_MEDIA_PREFIXES, MediaElement),
]

_ALL_ALLOWED_PREFIXES = tuple(p for prefixes, _ in _PREFIX_RULES for p in prefixes)

_CLASS_LABEL_SUFFIX = {
    InputElement: "Input",
    ButtonElement: "Button",
    TextElement: "Text",
    DropdownElement: "Dropdown",
    CheckboxElement: "Checkbox",
    TableElement: "Table",
    UploadElement: "Upload",
    ContainerElement: "Container",
    MediaElement: "Media",
}


def _humanize_locator_name(raw_name: str, matched_cls=None) -> str:
    """Converts a snake_case variable name (e.g. 'input_first_name') into a readable label ('First Name Input')."""
    lower_name = raw_name.lower()
    stripped = raw_name
    for prefix in sorted(_ALL_ALLOWED_PREFIXES, key=len, reverse=True):
        if lower_name.startswith(prefix):
            stripped = raw_name[len(prefix):]
            break
    words = [w.capitalize() for w in stripped.replace("_", " ").split() if w]
    base_label = " ".join(words) if words else raw_name.replace("_", " ").title()
    suffix = _CLASS_LABEL_SUFFIX.get(matched_cls, "Element")
    if base_label.lower().endswith(suffix.lower()):
        return base_label
    return f"{base_label} {suffix}"


def _parse_locator(by: str = None, value: str = None, **kwargs) -> tuple:
    if kwargs:
        if len(kwargs) != 1:
            raise ValueError("Specify exactly one locator strategy.")
        key, val = next(iter(kwargs.items()))
        if key not in _BY_MAP:
            raise ValueError(f"Unsupported locator strategy '{key}'. Allowed: {list(_BY_MAP.keys())}")
        return (_BY_MAP[key], val)
    if by and value is not None:
        return (by, value)
    raise ValueError("Provide either (by, value) or a keyword argument like id='...'.")


class FindByDescriptor:
    """
    Hybrid Descriptor and Decorator that resolves to a specialized element or full `UIElement`.
    Validates variable naming conventions by prefix; if the expected prefix is missing,
    logs a warning and falls back to exposing all `UIElement` actions.
    """
    def __init__(
        self,
        locator: tuple,
        element_cls=None,
        expected_prefixes: tuple = None,
        label: str = None,
        anchor: bool = False,
        shadow: bool = False,
    ):
        self.locator = locator
        self.element_cls = element_cls
        self.expected_prefixes = expected_prefixes
        self.label = label
        self.anchor = anchor
        self.shadow = shadow
        self.raw_name = None
        self.name = label
        self._resolved_cls = UIElement
        self._warning_msg = None
        self._warned = False

    def _configure_name(self, raw_name: str, owner_name: str = "PageObject"):
        self.raw_name = raw_name
        lower_name = raw_name.lower()

        if self.expected_prefixes:
            if lower_name.startswith(self.expected_prefixes):
                self._resolved_cls = self.element_cls
                self._warning_msg = None
            else:
                self._resolved_cls = UIElement
                self._warning_msg = (
                    f"[NAMING CONVENTION] {owner_name}.{raw_name}: "
                    f"Se esperaba el prefijo {self.expected_prefixes} para {self.element_cls.__name__}. "
                    f"Se despliegan todas las acciones de UIElement por defecto."
                )
        else:
            matched_cls = None
            for prefixes, cls in _PREFIX_RULES:
                if lower_name.startswith(prefixes):
                    matched_cls = cls
                    break
            if matched_cls:
                self._resolved_cls = matched_cls
                self._warning_msg = None
            else:
                self._resolved_cls = UIElement
                self._warning_msg = (
                    f"[NAMING CONVENTION] {owner_name}.{raw_name}: "
                    f"El nombre del locator no inicia con un prefijo estándar {_ALL_ALLOWED_PREFIXES}. "
                    f"Se despliegan todas las acciones de UIElement por defecto."
                )

        # Auto-humanize label if not explicitly provided
        self.name = self.label if self.label else _humanize_locator_name(raw_name, self._resolved_cls)

    def __set_name__(self, owner, name: str):
        self._configure_name(name, owner.__name__)
        if self.anchor:
            if "_page_anchors" not in owner.__dict__:
                owner._page_anchors = list(getattr(owner, "_page_anchors", []))
            if name not in owner._page_anchors:
                owner._page_anchors.append(name)

    def __call__(self, func):
        self._configure_name(func.__name__)
        return self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._warning_msg and not self._warned:
            instance.logger.warning(self._warning_msg)
            self._warned = True

        cache = getattr(instance, "_locator_element_cache", None)
        if cache is None:
            cache = {}
            instance._locator_element_cache = cache

        cache_key = (self.raw_name or id(self), id(instance.driver))
        if cache_key not in cache:
            cache[cache_key] = self._resolved_cls(
                instance.driver,
                self.locator,
                page_object=instance,
                locator_name=self.name,
                shadow=self.shadow,
            )
        return cache[cache_key]


def find_input(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> InputElement:
    """Defines a locator for an input/form field (Expected prefixes: _INPUT_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), InputElement, _INPUT_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_button(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> ButtonElement:
    """Defines a locator for a button/link/icon/clickable element (Expected prefixes: _BUTTON_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), ButtonElement, _BUTTON_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_text(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> TextElement:
    """Defines a locator for a label/text/message/header/badge element (Expected prefixes: _TEXT_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), TextElement, _TEXT_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_dropdown(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> DropdownElement:
    """Defines a locator for a dropdown/select/combo element (Expected prefixes: _DROPDOWN_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), DropdownElement, _DROPDOWN_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_checkbox(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> CheckboxElement:
    """Defines a locator for a checkbox/radio/toggle/switch element (Expected prefixes: _CHECKBOX_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), CheckboxElement, _CHECKBOX_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_table(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> TableElement:
    """Defines a locator for a table/grid element (Expected prefixes: _TABLE_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), TableElement, _TABLE_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_upload(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> UploadElement:
    """Defines a locator for a file upload element (Expected prefixes: _UPLOAD_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), UploadElement, _UPLOAD_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_container(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> ContainerElement:
    """Defines a locator for a modal/dialog/card/panel/loader/container element (Expected prefixes: _CONTAINER_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), ContainerElement, _CONTAINER_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_media(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> MediaElement:
    """Defines a locator for an image/logo/avatar/video/canvas element (Expected prefixes: _MEDIA_PREFIXES)."""
    return FindByDescriptor(_parse_locator(by, value, **kwargs), MediaElement, _MEDIA_PREFIXES, label=label, anchor=anchor, shadow=shadow)


def find_by(by: str = None, value: str = None, label: str = None, anchor: bool = False, shadow: bool = False, **kwargs) -> UIElement:
    """
    Defines a generic `UIElement` locator (exposes all actions in IDE; warns if prefix is missing).
    Optional `label` overrides the variable name in action logs; `anchor=True` marks the element
    as a page-readiness anchor checked by `is_loaded()` / `wait_until_loaded()`.
    Set `shadow=True` to explicitly force deep Shadow DOM piercing.
    """
    return FindByDescriptor(_parse_locator(by, value, **kwargs), label=label, anchor=anchor, shadow=shadow)

