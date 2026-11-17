"""
Sandbox Page Object for Actions Health Check.
Models all interactive widgets of the /sandbox playground following the strict 3-Layer Granular POM standard.
"""
from typing import Self, Optional, List, Dict, Any
from core.ui.common.base_page import BasePage
from core.ui.common.find_by import find_by


class SandboxPage(BasePage):
    PAGE_PATH = "/sandbox"

    # =========================================================================
    # CAPA 1: IDENTIDAD Y LOCALIZADORES
    # =========================================================================
    hdr_sandbox = find_by(id="sandbox-header", label="Sandbox Header", anchor=True)

    # Inputs & Typing
    input_username = find_by(id="inp-username", label="Nombre de Usuario")
    input_password = find_by(id="inp-password", label="Contraseña")
    input_clearable = find_by(id="inp-clearable", label="Input Borrable")
    input_comments = find_by(id="inp-comments", label="Comentarios")
    btn_submit_inputs = find_by(id="btn-submit-inputs", label="Validar Inputs")
    lbl_input_result = find_by(id="lbl-input-result", label="Resultado Inputs")

    # Clicks & Gestures
    btn_single_click = find_by(id="btn-single-click", label="Click Simple")
    btn_double_click = find_by(id="btn-double-click", label="Doble Click")
    btn_right_click = find_by(id="btn-right-click", label="Right Click")
    box_hover = find_by(id="box-hover", label="Caja Hover")
    drag_source = find_by(id="drag-source", label="Elemento Arrastrable")
    drag_target = find_by(id="drag-target", label="Zona de Soltado")
    lbl_click_result = find_by(id="lbl-click-result", label="Resultado Clicks")

    # Dropdowns & Selects
    ddl_country = find_by(id="ddl-country", label="Selector País")
    ddl_multi = find_by(id="ddl-multi", label="Selector Múltiple")
    lbl_dropdown_result = find_by(id="lbl-dropdown-result", label="Resultado Dropdown")

    # Checkboxes & Radios
    chk_terms = find_by(id="chk-terms", label="Aceptar Términos")
    chk_newsletter = find_by(id="chk-newsletter", label="Boletín")
    rdo_standard = find_by(id="rdo-standard", label="Envío Estándar")
    rdo_express = find_by(id="rdo-express", label="Envío Express")
    lbl_checkbox_result = find_by(id="lbl-checkbox-result", label="Resultado Checkboxes")

    # Tables & Grids
    tbl_customers = find_by(id="tbl-customers", label="Tabla Clientes")
    btn_edit_101 = find_by(id="btn-edit-101", label="Editar Cliente 101")
    lbl_table_action_result = find_by(id="lbl-table-action-result", label="Resultado Tabla")

    # Upload
    upl_document = find_by(id="upl-document", label="Subida de Archivo")
    lbl_upload_filename = find_by(id="lbl-upload-filename", label="Nombre Archivo Subido")

    # Dialogs & Modals
    btn_trigger_alert = find_by(id="btn-trigger-alert", label="Disparar Alert")
    btn_trigger_confirm = find_by(id="btn-trigger-confirm", label="Disparar Confirm")
    btn_trigger_prompt = find_by(id="btn-trigger-prompt", label="Disparar Prompt")
    btn_open_modal = find_by(id="btn-open-modal", label="Abrir Modal")
    btn_close_modal = find_by(id="btn-close-modal", label="Cerrar Modal")
    lbl_dialog_result = find_by(id="lbl-dialog-result", label="Resultado Diálogo")
    mdl_dialog = find_by(id="mdl-sandbox-dialog", label="Contenedor Modal")

    # Async CRUD (Protocolo Loaders & Toasts)
    inp_crud_entity = find_by(id="inp-crud-entity-name", label="Nombre Entidad CRUD")
    btn_save_crud = find_by(id="btn-save-crud", label="Guardar Registro CRUD")
    spn_crud_loader = find_by(id="spn-crud-loader", label="Spinner Overlay CRUD")
    toast_notification = find_by(id="toast-crud-notification", label="Notificación Toast")
    lbl_crud_status = find_by(id="lbl-crud-status", label="Estado CRUD")

    # IFrame & Tabs
    frame_sandbox = find_by(id="frame-sandbox", label="IFrame Sandbox")
    lnk_open_new_tab = find_by(id="lnk-open-new-tab", label="Enlace Nueva Pestaña")

    # Scroll
    box_scrollable = find_by(id="box-scrollable", label="Contenedor Scrollable")
    anchor_scroll_bottom = find_by(id="anchor-scroll-bottom", label="Ancla Fondo")
    btn_bottom_scroll = find_by(id="btn-bottom-scroll-action", label="Botón Fondo Scroll")
    lbl_scroll_result = find_by(id="lbl-scroll-result", label="Resultado Scroll")

    # Storage & Cookies
    btn_set_storage = find_by(id="btn-set-storage", label="Guardar Storage")
    btn_clear_storage = find_by(id="btn-clear-storage", label="Limpiar Storage")
    lbl_storage_token = find_by(id="lbl-storage-token", label="Token Storage")
    lbl_cookie_value = find_by(id="lbl-cookie-value", label="Valor Cookie")

    # 13. Autocomplete con Debounce
    inp_autocomplete = find_by(id="inp-autocomplete", label="Búsqueda Autocomplete")
    spn_autocomplete = find_by(id="spn-autocomplete", label="Spinner Autocomplete")
    box_autocomplete_list = find_by(id="box-autocomplete-list", label="Lista Autocomplete")
    btn_autocomplete_item = find_by(
        xpath="//div[@id='box-autocomplete-list']//div[contains(@class, 'suggestion-item') and contains(text(), '{item_name}')]",
        label="Item Autocomplete {item_name}"
    )
    lbl_autocomplete_result = find_by(id="lbl-autocomplete-result", label="Resultado Autocomplete")

    # 14. Datepicker & Sliders
    inp_date_display = find_by(id="inp-date-display", label="Input Fecha")
    btn_toggle_calendar = find_by(id="btn-toggle-calendar", label="Abrir Calendario")
    box_calendar_popover = find_by(id="box-calendar-popover", label="Popover Calendario")
    btn_calendar_day = find_by(
        xpath="//div[@id='box-calendar-popover']//button[@data-day='{day}']",
        label="Día Calendario {day}"
    )
    lbl_date_result = find_by(id="lbl-date-result", label="Resultado Fecha")
    rng_volume_slider = find_by(id="rng-volume-slider", label="Slider Volumen")
    lbl_slider_result = find_by(id="lbl-slider-result", label="Resultado Slider")

    # 15. Formulario Multi-Paso (Wizard)
    tab_step_1 = find_by(id="tab-step-1", label="Pestaña Paso 1")
    tab_step_2 = find_by(id="tab-step-2", label="Pestaña Paso 2")
    tab_step_3 = find_by(id="tab-step-3", label="Pestaña Paso 3")
    inp_wizard_email = find_by(id="inp-wizard-email", label="Email Wizard")
    btn_wizard_next_1 = find_by(id="btn-wizard-next-1", label="Siguiente Paso 1")
    inp_wizard_username = find_by(id="inp-wizard-username", label="Username Wizard")
    btn_wizard_prev_2 = find_by(id="btn-wizard-prev-2", label="Atrás Paso 2")
    btn_wizard_next_2 = find_by(id="btn-wizard-next-2", label="Siguiente Paso 2")
    lbl_wizard_summary = find_by(id="lbl-wizard-summary", label="Resumen Wizard")
    btn_wizard_prev_3 = find_by(id="btn-wizard-prev-3", label="Atrás Paso 3")
    btn_wizard_finish = find_by(id="btn-wizard-finish", label="Finalizar Wizard")
    lbl_wizard_result = find_by(id="lbl-wizard-result", label="Resultado Wizard")

    # 16. Resiliencia & Stale Element
    btn_recreate_node = find_by(id="btn-recreate-node", label="Recrear Nodo DOM")
    btn_stale_target = find_by(id="btn-stale-target", label="Botón Volátil Stale")
    lbl_stale_result = find_by(id="lbl-stale-result", label="Resultado Stale")

    # 17. Descarga de Archivos
    lnk_download_csv = find_by(id="lnk-download-csv", label="Enlace Descarga CSV")
    lbl_download_status = find_by(id="lbl-download-status", label="Estado Descarga")

    # 18. Portapapeles & Keys
    inp_copy_source = find_by(id="inp-copy-source", label="Token Origen")
    btn_copy_clipboard = find_by(id="btn-copy-clipboard", label="Copiar Token")
    inp_paste_target = find_by(id="inp-paste-target", label="Pegar Token")
    btn_validate_token = find_by(id="btn-validate-token", label="Validar Token")
    lbl_clipboard_result = find_by(id="lbl-clipboard-result", label="Resultado Portapapeles")

    # =========================================================================
    # CAPA 2: MÉTODOS ATÓMICOS GRANULARES
    # =========================================================================
    def set_username(self, username: str) -> Self:
        self.input_username.type(username)
        return self

    def set_password(self, password: str) -> Self:
        self.input_password.type_encrypted(password)
        return self

    def clear_clearable_input(self) -> Self:
        self.input_clearable.clear()
        return self

    def get_clearable_value(self) -> str:
        return self.input_clearable.get_value()

    def set_comments(self, comments: str) -> Self:
        self.input_comments.type(comments)
        return self

    def click_submit_inputs(self) -> Self:
        self.btn_submit_inputs.click()
        return self

    def get_input_result_text(self) -> str:
        return self.lbl_input_result.get_text()

    # Clicks
    def click_single(self) -> Self:
        self.btn_single_click.click()
        return self

    def click_double(self) -> Self:
        self.btn_double_click.double_click()
        return self

    def click_right(self) -> Self:
        self.btn_right_click.right_click()
        return self

    def hover_box(self) -> Self:
        self.box_hover.hover()
        return self

    def get_hover_box_text(self) -> str:
        return self.box_hover.get_text()

    def get_click_result_text(self) -> str:
        return self.lbl_click_result.get_text()

    # Dropdowns
    def select_country_by_text(self, text: str) -> Self:
        self.ddl_country.select_by_text(text)
        return self

    def select_country_by_value(self, val: str) -> Self:
        self.ddl_country.select_by_value(val)
        return self

    def select_country_by_index(self, index: int) -> Self:
        self.ddl_country.select_by_index(index)
        return self

    def get_selected_country(self) -> str:
        return self.ddl_country.get_selected_text()

    def get_dropdown_result_text(self) -> str:
        return self.lbl_dropdown_result.get_text()

    # Checkboxes & Radios
    def check_terms(self) -> Self:
        self.chk_terms.check(True)
        return self

    def uncheck_terms(self) -> Self:
        self.chk_terms.check(False)
        return self

    def is_terms_checked(self) -> bool:
        return self.chk_terms.is_checked()

    def select_shipping_express(self) -> Self:
        self.rdo_express.select_radio()
        return self

    def is_shipping_express_selected(self) -> bool:
        return self.rdo_express.is_selected()

    # Table
    def get_table_row_count(self) -> int:
        return self.tbl_customers.get_row_count()

    def get_table_cell(self, row: int, col: int) -> str:
        return self.tbl_customers.get_cell_text(row, col)

    def click_edit_customer_101(self) -> Self:
        self.btn_edit_101.click()
        return self

    def get_table_action_result(self) -> str:
        return self.lbl_table_action_result.get_text()

    # Upload
    def upload_test_document(self, file_path: str) -> Self:
        self.upl_document.upload_file(file_path)
        return self

    def get_uploaded_filename(self) -> str:
        return self.lbl_upload_filename.get_text()

    # Dialogs & Modals
    def open_html_modal(self) -> Self:
        self.btn_open_modal.click()
        self.mdl_dialog.wait_visible(5)
        return self

    def close_html_modal(self) -> Self:
        self.btn_close_modal.click()
        self.mdl_dialog.wait_disappear(5)
        return self

    def is_modal_visible(self) -> bool:
        return self.mdl_dialog.is_visible()

    # Scroll
    def scroll_to_bottom_action(self) -> Self:
        self.btn_bottom_scroll.scroll_to_center()
        return self

    def click_bottom_scroll_action(self) -> Self:
        self.btn_bottom_scroll.click()
        return self

    def get_scroll_result_text(self) -> str:
        return self.lbl_scroll_result.get_text()

    # Async CRUD
    def set_crud_entity_name(self, name: str) -> Self:
        self.inp_crud_entity.type(name)
        return self

    def click_save_crud(self) -> Self:
        self.btn_save_crud.click()
        return self

    def wait_for_crud_loader_to_disappear(self, timeout: int = 10) -> Self:
        self.spn_crud_loader.wait_disappear(timeout)
        return self

    def get_toast_message(self, timeout: int = 10) -> str:
        self.toast_notification.wait_visible(timeout)
        return self.toast_notification.get_text()

    # Storage
    def click_set_storage(self) -> Self:
        self.btn_set_storage.click()
        return self

    def click_clear_storage(self) -> Self:
        self.btn_clear_storage.click()
        return self

    def get_storage_token_display(self) -> str:
        return self.lbl_storage_token.get_text()

    def get_cookie_value_display(self) -> str:
        return self.lbl_cookie_value.get_text()

    # 13. Autocomplete
    def search_autocomplete(self, query: str) -> Self:
        self.inp_autocomplete.type(query)
        self.box_autocomplete_list.wait_visible(5)
        return self

    def select_autocomplete_item(self, item_name: str) -> Self:
        self.btn_autocomplete_item.format(item_name=item_name).click()
        return self

    def get_autocomplete_result_text(self) -> str:
        return self.lbl_autocomplete_result.get_text()

    # 14. Datepicker & Sliders
    def open_calendar(self) -> Self:
        self.btn_toggle_calendar.click()
        self.box_calendar_popover.wait_visible(3)
        return self

    def select_calendar_day(self, day: str) -> Self:
        self.btn_calendar_day.format(day=day).click()
        return self

    def get_date_display_value(self) -> str:
        return self.inp_date_display.get_value()

    def get_date_result_text(self) -> str:
        return self.lbl_date_result.get_text()

    def get_slider_result_text(self) -> str:
        return self.lbl_slider_result.get_text()

    # 15. Formulario Multi-Paso (Wizard)
    def set_wizard_email(self, email: str) -> Self:
        self.inp_wizard_email.type(email)
        return self

    def click_wizard_next_1(self) -> Self:
        self.btn_wizard_next_1.click()
        return self

    def set_wizard_username(self, username: str) -> Self:
        self.inp_wizard_username.type(username)
        return self

    def click_wizard_next_2(self) -> Self:
        self.btn_wizard_next_2.click()
        return self

    def click_wizard_finish(self) -> Self:
        self.btn_wizard_finish.click()
        return self

    def get_wizard_result_text(self) -> str:
        return self.lbl_wizard_result.get_text()

    # 16. Resiliencia & Stale Element
    def click_recreate_node(self) -> Self:
        self.btn_recreate_node.click()
        return self

    def click_stale_target(self) -> Self:
        self.btn_stale_target.click()
        return self

    def get_stale_result_text(self) -> str:
        return self.lbl_stale_result.get_text()

    # 17. Descarga de Archivos
    def click_download_csv(self) -> Self:
        self.lnk_download_csv.click()
        return self

    def get_download_status_text(self) -> str:
        return self.lbl_download_status.get_text()

    # 18. Portapapeles & Keys
    def get_copy_source_value(self) -> str:
        return self.inp_copy_source.get_value()

    def click_copy_clipboard(self) -> Self:
        self.btn_copy_clipboard.click()
        return self

    def set_paste_token(self, token: str) -> Self:
        self.inp_paste_target.type(token)
        return self

    def click_validate_token(self) -> Self:
        self.btn_validate_token.click()
        return self

    def get_clipboard_result_text(self) -> str:
        return self.lbl_clipboard_result.get_text()

    # =========================================================================
    # CAPA 3: MÉTODOS COMPUESTOS DE NEGOCIO Y FORMULARIOS
    # =========================================================================
    def execute_complete_inputs_flow(self, username: str, password: str, comments: str) -> Self:
        """Composite method verifying full input form flow."""
        return (
            self.set_username(username)
                .set_password(password)
                .set_comments(comments)
                .click_submit_inputs()
        )

    def execute_async_crud_flow(self, entity_name: str) -> Self:
        """
        Composite method strictly following CRUD Protocol (Rule 7).
        Enforces internal loader synchronization before returning self.
        """
        return (
            self.set_crud_entity_name(entity_name)
                .click_save_crud()
                .wait_for_crud_loader_to_disappear()  # Internal auto-sync
        )

    def execute_autocomplete_selection(self, query: str, item_name: str) -> Self:
        """Composite method verifying async debounce search and selection."""
        return (
            self.search_autocomplete(query)
                .select_autocomplete_item(item_name)
        )

    def execute_wizard_complete_flow(self, email: str, username: str) -> Self:
        """Composite method guiding user through 3-step wizard."""
        return (
            self.set_wizard_email(email)
                .click_wizard_next_1()
                .set_wizard_username(username)
                .click_wizard_next_2()
                .click_wizard_finish()
        )

    def execute_clipboard_token_verification(self, token: str) -> Self:
        """Composite method verifying token paste and validation."""
        return (
            self.set_paste_token(token)
                .click_validate_token()
        )

