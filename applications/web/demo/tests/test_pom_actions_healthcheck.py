"""
Comprehensive Page Object & Actions Health Check Test Suite.
Validates 100% of the Page Object methods and ActionFactory capabilities against the local /sandbox playground.
"""
import os
import tempfile
import allure
import pytest
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
@allure.epic("Framework Certification")
@allure.feature("Page Object Health Check")
class TestPOMActionsHealthCheck(BaseTest):

    SANDBOX_URL = "http://127.0.0.1:5000/sandbox"

    def _ensure_sandbox_loaded(self):
        """Helper to navigate to sandbox and assert anchor readiness."""
        if not self.driver.current_url.endswith("/sandbox"):
            self.driver.get(self.SANDBOX_URL)
        self.app.sandbox_page.wait_until_loaded(timeout=10)

    @test_case(id="HC-POM-001")
    @allure.story("HC-01: Inputs, Typing, Password Encryption & Clear")
    def test_healthcheck_inputs_typing_and_clearing(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Probar limpieza de campo previo"):
            page.clear_clearable_input()
            actual_clear = page.get_clearable_value()
            assert actual_clear == "", f"Expected empty input after clear(), but got '{actual_clear}'"

        with allure.step("2. Acción: Escribir credenciales y comentarios"):
            page.set_username(data["username"])
            page.set_password(data["password"])
            page.set_comments(data["comments"])
            page.click_submit_inputs()

        with allure.step("3. Verificación: Confirmar reflejo de validación"):
            actual_res = page.get_input_result_text()
            expected_res = expected["input_validation_result"]
            assert actual_res == expected_res, f"Expected '{expected_res}', but got '{actual_res}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-02: Clicks, Doble Click, Right Click & Hover")
    def test_healthcheck_clicks_and_mouse_gestures(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Click simple"):
            page.click_single()
            actual = page.get_click_result_text()
            assert actual == expected["single_click_result"], f"Expected '{expected['single_click_result']}', got '{actual}'"

        with allure.step("2. Acción: Doble click"):
            page.click_double()
            actual = page.get_click_result_text()
            assert actual == expected["double_click_result"], f"Expected '{expected['double_click_result']}', got '{actual}'"

        with allure.step("3. Acción: Right click (Context Menu)"):
            page.click_right()
            actual = page.get_click_result_text()
            assert actual == expected["right_click_result"], f"Expected '{expected['right_click_result']}', got '{actual}'"

        with allure.step("4. Acción: Hover con cursor"):
            page.hover_box()
            hover_text = page.get_hover_box_text()
            assert "Hover detectado" in hover_text, f"Expected hover confirmation, got '{hover_text}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-03: Dropdowns, Checkboxes & Radio Groups")
    def test_healthcheck_dropdowns_and_checkboxes(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Selección de Dropdown por texto visible"):
            page.select_country_by_text(data["country_text"])
            actual_ddl = page.get_dropdown_result_text()
            assert actual_ddl == expected["dropdown_result"], f"Expected '{expected['dropdown_result']}', got '{actual_ddl}'"

        with allure.step("2. Acción: Marcar checkbox"):
            page.check_terms()
            assert page.is_terms_checked() is True, "Checkbox terms should be checked"

        with allure.step("3. Acción: Desmarcar checkbox"):
            page.uncheck_terms()
            assert page.is_terms_checked() is False, "Checkbox terms should be unchecked"

        with allure.step("4. Acción: Seleccionar Radio Button Express"):
            page.select_shipping_express()
            assert page.is_shipping_express_selected() is True, "Radio Express should be selected"

    @test_case(id="HC-POM-001")
    @allure.story("HC-04: Data Tables & File Upload")
    def test_healthcheck_tables_and_file_upload(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Verificación: Conteo de filas en tabla"):
            rows = page.get_table_row_count()
            assert rows == expected["table_rows"], f"Expected {expected['table_rows']} rows, got {rows}"

        with allure.step("2. Verificación: Lectura de celda (Fila 1, Columna 2)"):
            cell_text = page.get_table_cell(1, 2)
            assert cell_text == "Alice Smith", f"Expected 'Alice Smith', got '{cell_text}'"

        with allure.step("3. Acción: Click en botón dentro de la tabla"):
            page.click_edit_customer_101()
            actual_tbl_action = page.get_table_action_result()
            assert actual_tbl_action == expected["table_edit_action"]

        with allure.step("4. Acción: Subida de archivo (File Upload)"):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                tmp.write(b"Healthcheck audit test file payload")
                tmp_path = tmp.name

            try:
                page.upload_test_document(tmp_path)
                filename = os.path.basename(tmp_path)
                actual_uploaded = page.get_uploaded_filename()
                assert actual_uploaded == filename, f"Expected '{filename}', got '{actual_uploaded}'"
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    @test_case(id="HC-POM-001")
    @allure.story("HC-05: Scroll, Viewport & Localización Espacial")
    def test_healthcheck_scroll_and_viewport(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Desplazamiento a elemento en fondo del contenedor"):
            page.scroll_to_bottom_action()
            page.click_bottom_scroll_action()

        with allure.step("2. Verificación: Confirmar interacción con elemento scrolleado"):
            actual = page.get_scroll_result_text()
            assert actual == expected["scroll_action_result"]

    @test_case(id="HC-POM-001")
    @allure.story("HC-06: Protocolo CRUD (Auto-Sincronización Loader & Toast)")
    def test_healthcheck_async_crud_loaders_and_toasts(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Ejecutar flujo compuesto CRUD con auto-espera del spinner"):
            # Enforces Rule 7: Internal wait_for_crud_loader_to_disappear() before returning
            page.execute_async_crud_flow(data["crud_entity"])

        with allure.step("2. Verificación: Confirmar notificación Toast de éxito"):
            actual_toast = page.get_toast_message(timeout=10)
            expected_toast = expected["crud_toast_message"]
            assert actual_toast == expected_toast, f"Expected toast '{expected_toast}', but got '{actual_toast}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-07: HTML Modal Dialogs")
    def test_healthcheck_html_modal_dialogs(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page

        with allure.step("1. Acción: Abrir diálogo modal HTML"):
            page.open_html_modal()
            assert page.is_modal_visible() is True, "Modal should be visible after click"

        with allure.step("2. Acción: Cerrar diálogo modal HTML"):
            page.close_html_modal()
            assert page.is_modal_visible() is False, "Modal should be closed after click"

    @test_case(id="HC-POM-001")
    @allure.story("HC-08: Storage & Cookies Management")
    def test_healthcheck_storage_and_cookies(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Guardar token en localStorage y cookie en navegador"):
            page.click_set_storage()
            actual_token = page.get_storage_token_display()
            actual_cookie = page.get_cookie_value_display()
            assert actual_token == expected["storage_token"], f"Expected token '{expected['storage_token']}', got '{actual_token}'"
            assert actual_cookie == expected["cookie_value"], f"Expected cookie '{expected['cookie_value']}', got '{actual_cookie}'"

        with allure.step("2. Acción: Limpiar storage"):
            page.click_clear_storage()
            assert page.get_storage_token_display() == "None"
            assert page.get_cookie_value_display() == "None"

    @test_case(id="HC-POM-001")
    @allure.story("HC-09: Autocomplete & Debounce AJAX Selection")
    def test_healthcheck_autocomplete_debounce(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Búsqueda con debounce y selección de framework"):
            page.execute_autocomplete_selection(data["autocomplete_query"], data["autocomplete_selection"])

        with allure.step("2. Verificación: Confirmar selección reflejada"):
            actual = page.get_autocomplete_result_text()
            assert actual == expected["autocomplete_result"], f"Expected '{expected['autocomplete_result']}', got '{actual}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-10: Datepicker Popover & Interactive Sliders")
    def test_healthcheck_datepicker_and_sliders(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Abrir popover de calendario y elegir día"):
            page.open_calendar()
            page.select_calendar_day(data["calendar_day"])

        with allure.step("2. Verificación: Validar fecha seleccionada en input y badge"):
            actual_display = page.get_date_display_value()
            actual_result = page.get_date_result_text()
            assert actual_display == expected["calendar_date_display"], f"Expected '{expected['calendar_date_display']}', got '{actual_display}'"
            assert actual_result == expected["calendar_date_result"], f"Expected '{expected['calendar_date_result']}', got '{actual_result}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-11: Wizard Multi-Paso (Form Stepper)")
    def test_healthcheck_multi_step_wizard(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        data = self.get_data_for_test()
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Completar flujo de 3 pasos del wizard"):
            page.execute_wizard_complete_flow(data["wizard_email"], data["wizard_user"])

        with allure.step("2. Verificación: Confirmar mensaje de finalización"):
            actual = page.get_wizard_result_text()
            assert actual == expected["wizard_completed_result"], f"Expected '{expected['wizard_completed_result']}', got '{actual}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-12: Resiliencia DOM ante Stale Element")
    def test_healthcheck_stale_element_resilience(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Click en botón volátil inicial"):
            page.click_stale_target()
            assert page.get_stale_result_text() == expected["stale_click_result"]

        with allure.step("2. Acción: Disparar destrucción y re-creación de nodo en DOM"):
            page.click_recreate_node()

        with allure.step("3. Acción y Verificación: Interactuar con el nodo recreado"):
            page.click_stale_target()
            actual = page.get_stale_result_text()
            assert actual == expected["stale_click_result"], f"Expected '{expected['stale_click_result']}', got '{actual}'"

    @test_case(id="HC-POM-001")
    @allure.story("HC-13: Portapapeles & Verificación de Token")
    def test_healthcheck_clipboard_and_token_validation(self):
        self._ensure_sandbox_loaded()
        page = self.app.sandbox_page
        expected = self.get_expected_for_test()

        with allure.step("1. Acción: Leer token origen"):
            token = page.get_copy_source_value()
            assert len(token) > 0, "Token should not be empty"

        with allure.step("2. Acción: Pegar token en campo de validación y enviar"):
            page.execute_clipboard_token_verification(token)

        with allure.step("3. Verificación: Confirmar match exitoso"):
            actual = page.get_clipboard_result_text()
            assert actual == expected["clipboard_verified_result"], f"Expected '{expected['clipboard_verified_result']}', got '{actual}'"

