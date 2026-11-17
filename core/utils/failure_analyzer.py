"""
Smart Failure Analyzer & Root-Cause Classifier.

Categorizes test failures into plain-language diagnostics for QA analysts,
developers, and product owners:
1. Business Logic Defect (AssertionError / Oracle mismatch)
2. Element Not Found in DOM (NoSuchElementException)
3. Invalid Selector Syntax (InvalidSelectorException / XPath syntax errors)
4. Synchronization Timeout (TimeoutException / SLA exceeded)
5. Interaction Blocked in UI (ElementClickIntercepted / NotInteractable)
6. Backend / Service Error (5xx HTTP / Network disconnect)
7. System / Automation Script Error (AttributeError, KeyError, etc.)
"""

import os
import re
import traceback
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    InvalidSelectorException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
)


@dataclass
class FailureDiagnostic:
    """Structured failure diagnosis representation."""
    category_id: str
    category_name: str
    category_badge_color: str
    summary: str
    root_cause: str
    suggested_action: str
    test_id: str = "N/A"
    test_name: str = "N/A"
    current_url: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    failed_selector: Optional[str] = None
    selector_method: Optional[str] = None
    blocking_element: Optional[str] = None
    raw_exception_type: str = ""
    raw_exception_message: str = ""
    screenshot_path: Optional[str] = None
    extra_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "category_badge_color": self.category_badge_color,
            "summary": self.summary,
            "root_cause": self.root_cause,
            "suggested_action": self.suggested_action,
            "current_url": self.current_url,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "failed_selector": self.failed_selector,
            "selector_method": self.selector_method,
            "blocking_element": self.blocking_element,
            "raw_exception_type": self.raw_exception_type,
            "raw_exception_message": self.raw_exception_message,
            "screenshot_path": self.screenshot_path,
            "extra_details": self.extra_details,
        }

    def render_ascii_card(self) -> str:
        """Renders an ASCII card for terminal output and sequential logs."""
        w = 84
        border = "═" * (w - 2)
        sep = "─" * (w - 2)

        lines = [
            f"╔{border}╗",
            f"║ 🚨 DIAGNÓSTICO INTELIGENTE DE FALLO (ROOT CAUSE ANALYSIS){' ' * (w - 61)}║",
            f"╠{border}╣",
            f"║ • Test ID:         {self.test_id:<{w - 23}}║",
            f"║ • Test Name:       {self.test_name[:w - 24]:<{w - 23}}║",
            f"║ • Categoría:       {self.category_name:<{w - 23}}║",
        ]

        if self.current_url:
            lines.append(f"║ • URL al Fallar:   {self.current_url[:w - 24]:<{w - 23}}║")

        lines.append(f"╟{sep}╢")
        lines.append(f"║ 📌 CAUSA RAÍZ:{' ' * (w - 18)}║")
        for chunk in self._wrap_text(self.root_cause, w - 6):
            lines.append(f"║   {chunk:<{w - 6}}║")

        if self.expected_value or self.actual_value:
            lines.append(f"╟{sep}╢")
            if self.expected_value:
                exp = f"• Esperado (Oracle):  {self.expected_value}"
                for chunk in self._wrap_text(exp, w - 6):
                    lines.append(f"║   {chunk:<{w - 6}}║")
            if self.actual_value:
                act = f"• Obtenido (Real):    {self.actual_value}"
                for chunk in self._wrap_text(act, w - 6):
                    lines.append(f"║   {chunk:<{w - 6}}║")

        if self.failed_selector:
            lines.append(f"╟{sep}╢")
            sel_info = f"• Selector Fallido ({self.selector_method or 'Locator'}): {self.failed_selector}"
            for chunk in self._wrap_text(sel_info, w - 6):
                lines.append(f"║   {chunk:<{w - 6}}║")

        if self.blocking_element:
            lines.append(f"╟{sep}╢")
            blk = f"• Bloqueado por:      {self.blocking_element}"
            for chunk in self._wrap_text(blk, w - 6):
                lines.append(f"║   {chunk:<{w - 6}}║")

        lines.append(f"╟{sep}╢")
        lines.append(f"║ 💡 ACCIÓN SUGERIDA:{' ' * (w - 23)}║")
        for chunk in self._wrap_text(self.suggested_action, w - 6):
            lines.append(f"║   {chunk:<{w - 6}}║")

        lines.append(f"╚{border}╝")
        return "\n".join(lines)

    def render_html_card(self) -> str:
        """Renders an executive HTML widget suitable for Allure report attachment."""
        badge_style = f"background: {self.category_badge_color}; color: #ffffff; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 0.85rem;"
        
        expected_actual_html = ""
        if self.expected_value or self.actual_value:
            expected_actual_html = f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0;">
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 10px 14px; border-radius: 4px;">
                    <div style="font-weight: 700; color: #10b981; font-size: 0.8rem; text-transform: uppercase;">Valor Esperado (Oracle)</div>
                    <div style="font-family: monospace; font-size: 0.95rem; margin-top: 4px; word-break: break-all;">{self._escape_html(self.expected_value or 'N/A')}</div>
                </div>
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px 14px; border-radius: 4px;">
                    <div style="font-weight: 700; color: #ef4444; font-size: 0.8rem; text-transform: uppercase;">Valor Obtenido (En Pantalla)</div>
                    <div style="font-family: monospace; font-size: 0.95rem; margin-top: 4px; word-break: break-all;">{self._escape_html(self.actual_value or 'N/A')}</div>
                </div>
            </div>
            """

        selector_html = ""
        if self.failed_selector:
            selector_html = f"""
            <div style="background: #181b24; color: #f9fafb; padding: 12px 16px; border-radius: 6px; margin: 12px 0; font-family: monospace; font-size: 0.88rem; overflow-x: auto;">
                <span style="color: #ff004f; font-weight: 700;">// Selector Involucrado ({self._escape_html(self.selector_method or 'Locator')}):</span><br/>
                <code>{self._escape_html(self.failed_selector)}</code>
            </div>
            """

        blocking_html = ""
        if self.blocking_element:
            blocking_html = f"""
            <div style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b; padding: 10px 14px; border-radius: 4px; margin: 12px 0;">
                <strong style="color: #f59e0b;">Elemento que interceptó el clic:</strong>
                <pre style="margin: 4px 0 0; font-size: 0.82rem; white-space: pre-wrap;">{self._escape_html(self.blocking_element)}</pre>
            </div>
            """

        url_html = f"<div style='font-size: 0.82rem; color: #6b7280; margin-top: 4px;'><strong>URL al fallar:</strong> <code>{self._escape_html(self.current_url)}</code></div>" if self.current_url else ""

        return f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); max-width: 900px; color: #111827;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f3f4f6; padding-bottom: 14px; margin-bottom: 16px;">
                <div>
                    <h3 style="margin: 0; font-size: 1.18rem; font-weight: 800; color: #111827;">🚨 Diagnóstico Ejecutivo de Fallo (Root Cause Analysis)</h3>
                    <div style="font-size: 0.85rem; color: #6b7280; margin-top: 4px;">Test: <strong>{self._escape_html(self.test_id)}</strong> — <em>{self._escape_html(self.test_name)}</em></div>
                    {url_html}
                </div>
                <div>
                    <span style="{badge_style}">{self._escape_html(self.category_name)}</span>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-weight: 700; color: #374151; font-size: 0.9rem; margin-bottom: 6px;">📌 Causa Raíz Detectada:</div>
                <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 12px 16px; border-radius: 6px; font-size: 0.92rem; line-height: 1.55; color: #1f2937;">
                    {self._escape_html(self.root_cause)}
                </div>
            </div>

            {expected_actual_html}
            {selector_html}
            {blocking_html}

            <div style="background: rgba(79, 70, 229, 0.08); border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 4px; margin-top: 16px;">
                <strong style="color: #4f46e5; font-size: 0.88rem;">💡 Acción Sugerida para el Analista / Desarrollador:</strong>
                <div style="font-size: 0.9rem; color: #1e1b4b; margin-top: 4px; line-height: 1.5;">
                    {self._escape_html(self.suggested_action)}
                </div>
            </div>
        </div>
        """

    @staticmethod
    def _escape_html(text: str) -> str:
        if text is None:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )

    @staticmethod
    def _wrap_text(text: str, width: int):
        words = text.split()
        lines = []
        current = []
        current_len = 0
        for w in words:
            if current_len + len(w) + 1 <= width:
                current.append(w)
                current_len += len(w) + 1
            else:
                if current:
                    lines.append(" ".join(current))
                current = [w]
                current_len = len(w)
        if current:
            lines.append(" ".join(current))
        return lines or [""]


class FailureAnalyzer:
    """Intelligent Root-Cause Classifier for Selenium and Pytest test failures."""

    @classmethod
    def analyze(
        cls,
        exc_info,
        test_instance: Any = None,
        item: Any = None,
        driver: Any = None,
    ) -> FailureDiagnostic:
        """
        Classifies an exception and returns a rich FailureDiagnostic object.

        Args:
            exc_info: Pytest or Python exception info (sys.exc_info() or pytest.ExceptionInfo).
            test_instance: The BaseTest class instance if available.
            item: The Pytest Item object.
            driver: The Selenium WebDriver instance if available.
        """
        exc_type = getattr(exc_info, "type", None) or type(exc_info)
        exc_val = getattr(exc_info, "value", None) or exc_info
        raw_msg = str(exc_val)
        raw_type_name = getattr(exc_type, "__name__", str(exc_type))

        # Resolve context metadata
        test_id = getattr(test_instance, "_current_test_id", None)
        if not test_id and item:
            func = getattr(item, "function", None)
            test_id = getattr(func, "_test_id", None)
        test_id = test_id or "N/A"

        test_name = getattr(item, "name", "Unknown Test")
        if hasattr(item, "function") and hasattr(item.function, "_test_title"):
            test_name = item.function._test_title

        # Resolve WebDriver URL and Page Source if available
        active_driver = driver or getattr(test_instance, "driver", None)
        current_url = None
        if active_driver:
            try:
                current_url = active_driver.current_url
            except Exception:
                current_url = None

        # ---------------------------------------------------------------------
        # 1. CLASSIFICATION: Business Logic Defect (AssertionError)
        # ---------------------------------------------------------------------
        if issubclass(exc_type, AssertionError):
            expected, actual = cls._parse_assertion_values(raw_msg, test_instance)
            return FailureDiagnostic(
                category_id="BUSINESS_LOGIC_DEFECT",
                category_name="🎯 DEFECTO DE NEGOCIO (Aserción Fallida)",
                category_badge_color="#ef4444",
                summary="El resultado en pantalla o backend no coincide con el oráculo de prueba esperado.",
                root_cause=cls._format_assertion_root_cause(raw_msg, expected, actual),
                suggested_action="Reportar bug funcional al equipo de desarrollo. La aplicación no cumple el comportamiento esperado según la especificación de negocio.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                expected_value=expected,
                actual_value=actual,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 2. CLASSIFICATION: Invalid Selector Syntax (InvalidSelectorException)
        # ---------------------------------------------------------------------
        if issubclass(exc_type, InvalidSelectorException) or "xpath expression" in raw_msg.lower() or "syntax error" in raw_msg.lower():
            selector, method = cls._extract_selector_info(raw_msg)
            return FailureDiagnostic(
                category_id="INVALID_SELECTOR_SYNTAX",
                category_name="⚠️ SINTAXIS DE SELECTOR INVÁLIDA",
                category_badge_color="#f59e0b",
                summary="El XPath o selector CSS está mal construido y el navegador no puede interpretarlo.",
                root_cause=f"Error sintáctico en la expresión del localizador: {raw_msg.splitlines()[0] if raw_msg else 'Sintaxis inválida'}",
                suggested_action="Corregir la sintaxis del selector en el Page Object. Validar comillas, cierres de corchetes `[]` y funciones con el skill 'smart-selenium-locator-generator'.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                failed_selector=selector,
                selector_method=method,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 3. CLASSIFICATION: Element Not Found in DOM (NoSuchElementException)
        # ---------------------------------------------------------------------
        if issubclass(exc_type, NoSuchElementException) or "no such element" in raw_msg.lower():
            selector, method = cls._extract_selector_info(raw_msg)
            return FailureDiagnostic(
                category_id="ELEMENT_NOT_FOUND",
                category_name="🔍 ELEMENTO NO ENCONTRADO EN EL DOM",
                category_badge_color="#8b5cf6",
                summary="El elemento buscado no existe en el árbol HTML de la página activa.",
                root_cause=f"Selenium buscó el elemento con estrategia '{method or 'Locator'}' pero no encontró coincidencias en el DOM actual.",
                suggested_action="1. Verificar si la pantalla navegó a la URL correcta.\n2. Comprobar si el frontend cambió IDs/clases.\n3. Usar el skill 'smart-selenium-locator-generator' para generar un localizador semántico resiliente anclado al Label.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                failed_selector=selector,
                selector_method=method,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 4. CLASSIFICATION: Synchronization Timeout (TimeoutException)
        # ---------------------------------------------------------------------
        if issubclass(exc_type, TimeoutException) or "timed out" in raw_msg.lower():
            selector, method = cls._extract_selector_info(raw_msg)
            return FailureDiagnostic(
                category_id="SYNCHRONIZATION_TIMEOUT",
                category_name="⏳ TIEMPO DE ESPERA AGOTADO (Timeout / SLA)",
                category_badge_color="#3b82f6",
                summary="El elemento tardó más del tiempo límite configurado en renderizarse o cambiar de estado.",
                root_cause="Se superó el tiempo máximo de espera explícita (SLA). El elemento no llegó al estado esperado (visible, clickable o desaparición) dentro del timeout.",
                suggested_action="1. Verificar si el backend/API está experimentando latencia o error 500.\n2. Si la operación es pesada, incrementar el timeout localmente usando `.at(15)` o `.at(20)`.\n3. Asegurar que la acción previa detonó la carga esperada.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                failed_selector=selector,
                selector_method=method,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 5. CLASSIFICATION: Interaction Blocked (ElementClickIntercepted)
        # ---------------------------------------------------------------------
        if issubclass(exc_type, (ElementClickInterceptedException, ElementNotInteractableException)) or "click intercepted" in raw_msg.lower():
            blocking_el = cls._extract_blocking_element(raw_msg)
            return FailureDiagnostic(
                category_id="INTERACTION_BLOCKED",
                category_name="🚫 INTERACCIÓN BLOQUEADA EN PANTALLA",
                category_badge_color="#ec4899",
                summary="El elemento existe en el DOM pero no puede recibir clics porque otro elemento lo está cubriendo o está deshabilitado.",
                root_cause=f"Otro elemento de la interfaz (ej. modal, overlay oscuro, spinner de carga o toast) está recibiendo el clic en lugar del botón objetivo.",
                suggested_action="1. Esperar a que el spinner o modal desaparezca con `wait_disappear()` antes del clic.\n2. Hacer scroll al centro del elemento con `.scroll_to_center()`.\n3. Como alternativa de desbloqueo rápido, utilizar `.js_click()`.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                blocking_element=blocking_el,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 6. CLASSIFICATION: Stale Element Reference
        # ---------------------------------------------------------------------
        if issubclass(exc_type, StaleElementReferenceException) or "stale element reference" in raw_msg.lower():
            return FailureDiagnostic(
                category_id="STALE_ELEMENT",
                category_name="🔄 REFERENCIA OBSOLETA (Stale Element)",
                category_badge_color="#f97316",
                summary="El elemento fue re-renderizado por el framework frontend (React/Vue/Angular) mientras se interactuaba con él.",
                root_cause="El nodo del DOM al que hacía referencia Selenium fue destruido y reemplazado dinámicamente por JavaScript.",
                suggested_action="Acceder nuevamente a la propiedad del elemento a través del Page Object para forzar una nueva búsqueda fresca en el DOM.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 7. CLASSIFICATION: Backend Service or Browser Crash
        # ---------------------------------------------------------------------
        if issubclass(exc_type, WebDriverException) and ("connection refused" in raw_msg.lower() or "session deleted" in raw_msg.lower() or "chrome not reachable" in raw_msg.lower()):
            return FailureDiagnostic(
                category_id="BROWSER_CRASH",
                category_name="💥 CAÍDA DE DRIVER O NAVEGADOR",
                category_badge_color="#64748b",
                summary="El navegador web se cerró inesperadamente o se perdió la conexión con el WebDriver.",
                root_cause="Pérdida de sesión del navegador. Posible falta de memoria en el nodo de ejecución, crash del renderer o cierre forzado del proceso.",
                suggested_action="Revisar memoria disponible en el sistema. Si ocurre en Docker/CI, asegurar `--shm-size=2gb` y el flag `--disable-dev-shm-usage`.",
                test_id=test_id,
                test_name=test_name,
                current_url=current_url,
                raw_exception_type=raw_type_name,
                raw_exception_message=raw_msg,
            )

        # ---------------------------------------------------------------------
        # 8. CLASSIFICATION: System / Automation Script Error
        # ---------------------------------------------------------------------
        return FailureDiagnostic(
            category_id="SYSTEM_SCRIPT_ERROR",
            category_name="⚙️ ERROR DE CÓDIGO / CONFIGURACIÓN",
            category_badge_color="#475569",
            summary=f"Excepción de Python no controlada en el código del test o de la suite: {raw_type_name}.",
            root_cause=f"{raw_type_name}: {raw_msg.splitlines()[0] if raw_msg else 'Error inesperado'}",
            suggested_action="Revisar el código del test, imports, fixture o archivo de configuración YAML/JSON para corregir la excepción de Python.",
            test_id=test_id,
            test_name=test_name,
            current_url=current_url,
            raw_exception_type=raw_type_name,
            raw_exception_message=raw_msg,
        )

    @staticmethod
    def _parse_assertion_values(message: str, test_instance: Any = None) -> Tuple[Optional[str], Optional[str]]:
        """Parses expected vs actual from assert messages or framework templates."""
        expected = None
        actual = None

        # Pattern 1: Expected 'X', but got 'Y' (Standard framework template)
        m = re.search(r"expected\s*['\"]?(.*?)['\"]?,\s*but\s*got\s*['\"]?(.*?)['\"]?(?:\n|$)", message, re.I)
        if m:
            return m.group(1).strip(), m.group(2).strip()

        # Pattern 2: assert actual == expected
        m = re.search(r"assert\s+(.+?)\s*==\s*(.+?)(?:\n|$)", message)
        if m:
            actual = m.group(1).strip()
            expected = m.group(2).strip()
            return expected, actual

        # Pattern 3: Fallback to test expected_data if available
        if test_instance and hasattr(test_instance, "expected_data") and test_instance.expected_data:
            expected = str(test_instance.expected_data)

        if not actual and message:
            actual = message.splitlines()[0]

        return expected, actual

    @staticmethod
    def _format_assertion_root_cause(raw_msg: str, expected: Optional[str], actual: Optional[str]) -> str:
        first_line = raw_msg.splitlines()[0] if raw_msg else "La aserción booleana falló."
        if expected and actual:
            return f"Discrepancia de datos en aserción: Se esperaba '{expected}', pero la aplicación arrojó '{actual}'."
        return first_line

    @staticmethod
    def _extract_selector_info(message: str) -> Tuple[Optional[str], Optional[str]]:
        """Extracts selector and locator method from Selenium error messages."""
        selector = None
        method = None

        # Pattern: {"method":"css selector","selector":"#submit"}
        m = re.search(r'\{"method":"(.*?)","selector":"(.*?)"\}', message)
        if m:
            return m.group(2), m.group(1)

        # Pattern: with the xpath expression //input[...]
        m = re.search(r"xpath expression\s+(//[^\s,]+)", message, re.I)
        if m:
            return m.group(1), "xpath"

        # Pattern: for element ('xpath', '//button')
        m = re.search(r"for element\s*\((['\"])(.*?)\1,\s*(['\"])(.*?)\3\)", message)
        if m:
            return m.group(4), m.group(2)

        return selector, method

    @staticmethod
    def _extract_blocking_element(message: str) -> Optional[str]:
        """Extracts the blocking element description from click intercepted messages."""
        m = re.search(r"Other element would receive the click:\s*(<.*?>)", message, re.DOTALL)
        if m:
            return m.group(1).strip()
        return None

