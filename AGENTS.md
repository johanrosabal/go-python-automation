# Reglas Obligatorias del Framework de Automatización (UI POM & API EOM)

Este proyecto utiliza una arquitectura Enterprise estricta en Python + Selenium + Pytest + Allure. **Cualquier código generado o modificado por el agente DEBE cumplir sin excepción las siguientes leyes arquitectónicas:**

---

## 0. Estructura Obligatoria de Carpetas por Aplicación
- **PROHIBIDO** agregar lógica de negocio o Page Objects dentro de `core/`. El directorio `core/` es exclusivamente para el motor base del framework.
- **PROHIBIDO** inventar nombres de carpetas fuera del estándar dentro de `applications/`. Toda aplicación Web o API debe respetar estrictamente la siguiente jerarquía:

### A. Estructura de una Aplicación Web (`applications/web/<app_name>/`)
```text
applications/web/<app_name>/
├── __init__.py
├── app/
│   ├── __init__.py
│   ├── <app_name>_app.py       # Orquestador de la aplicación (Hereda de BaseApp, expone @property por cada Page)
│   └── db_manager.py           # (Opcional) Gestor de consultas SQL de la aplicación
├── components/                 # Widgets UI reutilizables (Heredan de BaseComponent, ej. sidebar_component.py)
│   └── __init__.py
├── config/
│   ├── __init__.py
│   └── environments/           # 1 archivo YAML independiente por ambiente
│       ├── dev.yaml
│       ├── qa.yaml
│       ├── uat.yaml
│       └── prod.yaml
├── data/
│   ├── __init__.py
│   ├── excel/                  # Matriz de Casos de Prueba en Excel (.xlsx) congruente con el JSON
│   └── json/                   # 1 archivo JSON por cada Test ID (<TEST_ID>.json)
├── fixtures/                   # Precondiciones reutilizables de Pytest (ej. preconditions.py)
│   └── __init__.py
├── pages/                      # Page Objects de 3 Capas (<nombre>_page.py, heredan de BasePage)
│   └── __init__.py
├── tests/                      # Suites de prueba (test_<feature>.py, heredan de BaseTest)
│   └── __init__.py
└── utils/
    ├── __init__.py
    └── decorators.py           # Decorador de la aplicación (ej. @demo -> project_config)
```

### B. Estructura de una Aplicación API (`applications/api/<app_name>/`)
```text
applications/api/<app_name>/
├── __init__.py
├── client.py                   # Orquestador de Endpoints (API Client)
├── config/
│   └── environments/           # Archivos YAML por ambiente (dev.yaml, qa.yaml, uat.yaml, prod.yaml)
├── data/                       # Archivos JSON de pruebas API organizados por ambiente/versión (<TEST_ID>.json)
├── endpoints/                  # Clases de Endpoints (<nombre>_endpoint.py, heredan de BaseEndpoint)
└── tests/                      # Suites de prueba API (test_<endpoint>.py, heredan de BaseAPITest)
```

---

## 1. Estándar de Page Object Model (Modelo Granular de 3 Capas)
Todo Page Object debe ubicarse en `applications/web/<app>/pages/<nombre>_page.py`, heredar de `BasePage` (`core.ui.common.base_page`) y estructurarse obligatoriamente en **3 Capas**:

### Capa 1 — Identidad de Página, Componentes y Localizadores (`find_by`)
- **PROHIBIDO** usar tuplas `(By.ID, "...")`, `driver.find_element(...)` o llamar `self.element(...)` dentro de los métodos.
- **PROHIBIDO** definir localizadores sin prefijo semántico. Todo localizador debe declararse como atributo de clase usando `find_by` (`from core.ui.common.find_by import find_by`) e iniciar con un prefijo oficial:
  - `InputElement`: `input_`, `inp_`, `field_`, `textarea_`, `search_`, `date_`
  - `ButtonElement`: `btn_`, `button_`, `lnk_`, `link_`, `ico_`, `icon_`, `tab_`, `menu_`, `nav_`
  - `TextElement`: `lbl_`, `label_`, `txt_`, `text_`, `hdr_`, `title_`, `msg_`, `err_`, `error_`, `badge_`, `alert_`, `toast_`
  - `DropdownElement`: `ddl_`, `select_`, `cmb_`, `combo_`, `dropdown_`
  - `CheckboxElement`: `chk_`, `checkbox_`, `rdo_`, `radio_`, `tgl_`, `toggle_`, `swt_`, `switch_`
  - `TableElement`: `tbl_`, `table_`, `grd_`, `grid_`
  - `UploadElement`: `upl_`, `upload_`, `file_`
  - `ContainerElement`: `mdl_`, `modal_`, `dlg_`, `dialog_`, `crd_`, `card_`, `pnl_`, `panel_`, `sec_`, `cnt_`, `frm_`, `ldr_`, `spn_`
  - `MediaElement`: `img_`, `image_`, `avatar_`, `logo_`, `vid_`, `cnv_`
- **Contrato de Carga (`PAGE_PATH` + `anchor=True`)**:
  - Declara `PAGE_PATH = "/ruta"` si la página tiene una ruta relativa conocida.
  - Marca con `anchor=True` los 1 o 2 elementos clave de la página en `find_by(..., anchor=True)` para habilitar `page.is_loaded()` y `page.wait_until_loaded()`.
- **Localizadores Dinámicos**: Decláralos en la Capa 1 con llaves `{placeholder}` en el selector y el `label`, y formatéalos en la Capa 2 con `.format(placeholder=valor)`.
- **Estrategia y Prioridad de Localizadores Resilientes**: Consulta y aplica siempre las reglas de [`.agents/skills/smart-selenium-locator-generator/SKILL.md`](file:///c:/ai/go-python-selenium-automation/.agents/skills/smart-selenium-locator-generator/SKILL.md) para priorizar identidad semántica (ID estático $\rightarrow$ Name $\rightarrow$ Label con ascenso progresivo de contenedores $\rightarrow$ aria-label $\rightarrow$ data-testid $\rightarrow$ XPath relativo $\rightarrow$ CSS) y rechazar categóricamente XPaths absolutos, clases dinámicas o índices posicionales (`nth-child`).
- **Componentes Reutilizables y Modales (`BaseComponent`)**: 
  - Para menús laterales, barras de navegación, encabezados, pies de página o **Modales Globales** (ej. Confirmación de Eliminación, Timeout de Sesión, Alertas Toast), hereda de `BaseComponent` en `components/<name>_component.py` y vincúlalos en el Page Object con `sidebar = component(SidebarComponent)`.
  - Los **Modales Propios de una Página** simples (< 4 campos) pueden modelarse dentro del Page Object con prefijo `mdl_`; si son complejos (Wizards, tablas internas), extráelos a `components/` siguiendo la matriz de decisión de [`.agents/skills/analyze-ui-component/SKILL.md`](file:///c:/ai/go-python-selenium-automation/.agents/skills/analyze-ui-component/SKILL.md).

### Capa 2 — Métodos Atómicos Granulares (`set_*`, `get_*`, `select_*`, `check_*`, `click_*`)
- **PROHIBIDO** inventar métodos que no existan en [`ui_element.py`](file:///c:/ai/go-python-selenium-automation/core/ui/actions/ui_element.py) o [`base_page.py`](file:///c:/ai/go-python-selenium-automation/core/ui/common/base_page.py). Consulta siempre el catálogo oficial en [`.agents/skills/create-page-object/SKILL.md`](file:///c:/ai/go-python-selenium-automation/.agents/skills/create-page-object/SKILL.md):
  - **Métodos comunes en todos los elementos**: `.format(**kwargs)`, `.at(timeout)`, `.wait_visible()`, `.wait_present()`, `.wait_clickable()`, `.wait_disappear()`, `.is_visible()`, `.is_not_visible()`, `.is_enabled()`, `.is_clickable()`, `.get_text()`, `.get_trimmed_text()`, `.get_value()`, `.get_attribute(attr)`, `.scroll_to()`, `.scroll_to_center()`, `.screenshot(name)`.
  - **`InputElement`**: `.type(text, clear=True)`, `.send_keys(text, clear=True)`, `.type_encrypted(text)`, `.type_js(text)`, `.type_by_character(text)`, `.clear()`, `.physical_clear()`, `.press_enter()`, `.press_tab()`, `.press_escape()`, `.get_value()`.
  - **`ButtonElement`**: `.click()`, `.double_click()`, `.right_click()`, `.hover()`, `.js_click()`, `.drag_and_drop(target)`.
  - **`TextElement`**: `.get_text()`, `.get_trimmed_text()`, `.all_texts()`, `.get_int()`, `.get_float()`, `.contains_text(t)`, `.wait_text_contains(t)`, `.wait_until_text_is(t)`.
  - **`DropdownElement`**: `.select_by_text(t)`, `.select_by_partial_text(t)`, `.select_by_value(v)`, `.select_by_index(i)`, `.get_selected_text()`, `.get_dropdown_options()`.
  - **`CheckboxElement`**: `.check(state=True)`, `.is_checked()`, `.select_radio()`, `.is_selected()`.
  - **`TableElement`**: `.get_cell_text(r, c)`, `.get_row_count()`, `.get_table_headers()`, `.get_table_data()`, `.table_check_row(i)`, `.table_click_button(r, c)`, `.table_wait_not_empty()`.
  - **`UploadElement`**: `.upload_file(file_path)`.
- Cada elemento interactivo de la Capa 1 debe tener sus propios métodos atómicos individuales:
  - **Escritura / Selección / Acción** (siempre retornan `self` con anotación `-> Self`):
    - `set_<campo>(self, valor: str) -> Self`
    - `select_<campo>(self, opcion: str) -> Self`
    - `check_<campo>(self) -> Self` / `uncheck_<campo>(self) -> Self`
    - `upload_<campo>(self, file_path: str) -> Self`
    - `click_<elemento>(self) -> Self`
  - **Lectura / Estado** (retornan el valor primitivo para aserciones):
    - `get_<campo>(self) -> str` (para inputs usa `.get_value()`, para textos `.get_text()`, para dropdowns `.get_selected_text()`)
    - `is_<campo>(self) -> bool` (para checkboxes usa `.is_checked()`, para visibilidad `.is_visible()`)

### Capa 3 — Métodos Compuestos de Negocio y Formularios
- Los métodos de flujo (ej. `login`, `fill_checkout_form`, `complete_order`) **NUNCA** deben llamar directamente a los localizadores (`self.input_*`). **DEBEN** encadenar los métodos atómicos de la Capa 2 (`self.set_username(u).set_password(p).click_login()`) o usar `self.fill_form(data)` / `self.get_form_values(fields)`.

---

## 2. Registro Obligatorio en el Orquestador (`App`)
- Toda nueva página creada debe registrarse como `@property` con *lazy loading* en el orquestador de la aplicación (ej. `applications/web/<app>/app/<app>_app.py`).
- **PROHIBIDO** instanciar Page Objects manualmente dentro de los archivos de test (`LoginPage(self.driver)`). En los tests siempre se accede mediante `self.app.<nombre>_page`.

---

## 3. Estándar de Archivos JSON y Matrices Excel de Casos de Prueba
- **Fase Previa en Excel (`data/excel/<app>_<feature>_test_cases.xlsx`)**: Antes de crear el Page Object y los tests de Pytest, se diseñan los escenarios estructurados en Excel siguiendo el skill [`.agents/skills/design-test-cases-excel/SKILL.md`](file:///c:/ai/go-python-selenium-automation/.agents/skills/design-test-cases-excel/SKILL.md) agrupados por *Features* coherentes (no archivos monolíticos).
- Todo archivo JSON de prueba (`data/json/<TEST_ID>.json`) debe tener congruencia 1:1 con la matriz de Excel, tener la raíz `"tests"` y separar estrictamente los datos de entrada (`"data"`) de los resultados esperados (`"expected"`), incluyendo metadatos y `"bugs"`:
  - `tests.id`, `tests.testCaseName`, `tests.title`, `tests.description`
  - `tests.owner`, `tests.epic`, `tests.feature`, `tests.story`, `tests.severity`, `tests.priority`, `tests.tag`
  - `tests.execution`: `{"enabled": true, "environments": ["dev", "qa", "uat", "prod"], "skip_reason": ""}`
  - `tests.preconditions`: `[...]`
  - `tests.link`: `{"url": "...", "name": "..."}`
  - `tests.bugs`: `[{"id": "BUG-...", "title": "...", "status": "OPEN", "url": "..."}]`
  - `tests.data`: `{...}` (Exclusivamente inputs del test)
  - `tests.expected`: `{...}` (Exclusivamente valores esperados / llaves de validación)

---

## 4. Estándar de Clases de Prueba (`tests/test_*.py`)
- Toda clase de prueba Web hereda de `BaseTest` (`core.ui.common.base_test`) y lleva el decorador de su aplicación (ej. `@demo`).
- **OBLIGATORIO**: Todo método de prueba lleva `@test_case(id="<TEST_ID>")` (`from core.utils.decorators import test_case`). El `id` conecta el test con `data/json/<TEST_ID>.json` e inyecta automáticamente en Allure el título, descripción, epic, feature, severity, bugs y tags.
- **OBLIGATORIO**: Toda fase del test se envuelve en bloques narrativos `with allure.step("...")` (1. Navegación $\rightarrow$ 2. Acción $\rightarrow$ 3. Sincronización $\rightarrow$ 4. Verificación).
- **PROHIBIDO**: Llamar a `self.app.<page>.element(...)` o usar tuplas `(By.ID, ...)` en los tests. Toda interacción debe ser a través de los métodos atómicos (Capa 2) o compuestos (Capa 3) del Page Object.
- **OBLIGATORIO**: Sincronización explícita (`wait_for_*`, `wait_until_loaded`, `wait_disappear`) antes de hacer aserciones.
- **OBLIGATORIO**: Mensajes descriptivos en cada `assert` (`assert actual == expected, f"Expected '{expected}', but got '{actual}'"`).
- Para leer los datos de entrada del JSON se usa `self.test_data.get("clave")` o `self.get_data_for_test()`.
- Para leer los resultados esperados del JSON se usa `expected = self.get_expected_for_test()` (o `self.expected_data`).
- Para configuración de ambiente se usa `self.config.get("clave.subclave")` desde `config/environments/{env}.yaml`.
- Para credenciales basadas en roles (`users.default_role` y `users.roles.<role>` en `config/environments/{env}.yaml`), se usa `self.get_user(role=None)`, `self.get_username(role=None)`, `self.get_password(role=None)` o `self.username` / `self.password` (que resuelven automáticamente el `default_role` y decodifican contraseñas con prefijos `b64:` o `ENC:`).
- Para conexiones a múltiples bases de datos (`databases.default_connection` y `databases.connections.<alias>` en `config/environments/{env}.yaml`), se usa `self.get_db(connection_name=None)` (o `self.app.db.connection("<alias>")`) con los métodos `.fetch_one(sql, params)`, `.fetch_all(sql, params)`, `.fetch_value(sql, params)` y `.execute(sql, params)`.
- **Precondiciones Reutilizables por Rol (`applications/web/<app>/fixtures/preconditions.py`)**:
  - Para pruebas funcionales posteriores al login (ej. catálogo, carrito, perfil, checkout), **NO** se repite el flujo de login en el cuerpo del test; se consume un fixture de precondición por rol: `@pytest.mark.usefixtures("as_<role>")` (ej. `as_standard_user`, `as_problem_user`, `as_error_user`).
  - Las precondiciones deben ser **conscientes de la sesión (*Session-Aware*)**:
    - En **Modo Aislamiento** (`persistent_session = False`, default): Cada método abre y cierra su propio navegador limpio.
    - En **Modo Persistente** (`persistent_session = True`): Si el siguiente test requiere el mismo rol, **reutiliza la sesión activa**; si requiere un rol diferente, realiza un **cambio de identidad (*Identity Switch*)** limpiando cookies y almacenamiento antes de autenticar al nuevo rol.

---

## 5. Estándar de Archivos YAML de Ambiente (`config/environments/{env}.yaml`)
- **PROHIBIDO** crear un archivo YAML único con ambientes anidados. Cada ambiente debe tener su archivo independiente: `dev.yaml`, `qa.yaml`, `uat.yaml`, `prod.yaml`.
- **PROHIBIDO** colocar datos de usuario en la raíz (`user:`, `invalid_user:`). Toda credencial pertenece a `users.roles.<rol>`.
- Las contraseñas en el YAML deben usar el esquema de seguridad por prefijo: `b64:<cadena>` (estándar), `ENC:<token>` (criptográfico con `.env`), o `${ENV_VAR:b64:...}`.
- Conexiones a bases de datos deben estructurarse bajo `databases.default_connection` y `databases.connections.<alias>`. Consulta siempre el skill oficial en [`.agents/skills/create-environment-yaml/SKILL.md`](file:///c:/ai/go-python-selenium-automation/.agents/skills/create-environment-yaml/SKILL.md).

---

## 6. Arquitectura de Precondiciones y Gestión de Sesión Inteligente (Session-Aware RBAC)
Para pruebas funcionales posteriores a la autenticación (catálogo, carrito, checkout, perfil, paneles de administración), **NUNCA** se debe repetir el flujo manual de login dentro del cuerpo del test. Se deben emplear fixtures de precondición por rol en `applications/web/<app>/fixtures/preconditions.py`.

### 6.1. Ciclo de Vida del Navegador: Aislamiento vs. Persistencia
El framework soporta dos estrategias de ejecución a través del atributo `persistent_session` en la clase de prueba:

1. **Modo Aislamiento (`persistent_session = False`, Default)**:
   - Cada método de prueba abre y cierra su propio navegador limpio (`driver.quit()`).
   - Al terminar el test, se destruyen las cookies y el almacenamiento local.
   - Si `test_1` usa `as_standard_user` y `test_2` usa `as_problem_user`, no existe riesgo de conflicto de sesión porque cada uno corre en un navegador virgen.

2. **Modo Persistente (`persistent_session = True`)**:
   - Todos los métodos de la clase comparten la **misma instancia de WebDriver**.
   - Acelera drásticamente la ejecución al evitar abrir y cerrar navegadores repetidamente.
   - Requiere que los fixtures de precondición sean **Session-Aware**.

### 6.2. Mecanismo de Decisión "Session-Aware" & Cambio de Identidad (Identity Switch)
Los fixtures de precondición deben implementar la lógica de tres vías de `authenticate_as_role(app, role)`:

```text
¿Existe sesión activa en la página objetivo?
 ├── SÍ, y el rol solicitado es el MISMO:
 │    └── REUTILIZACIÓN DE SESIÓN (Skip login, conserva estado y acelera el test)
 ├── SÍ, pero el rol solicitado es DIFERENTE:
 │    └── IDENTITY SWITCH (Limpia cookies y local storage -> Autentica con el nuevo rol)
 └── NO:
      └── LOGIN INICIAL (Navega a login -> Autentica con el rol solicitado desde YAML)
```

### 6.3. Catálogo Estándar de Fixtures por Rol
En `applications/web/<app>/fixtures/preconditions.py`, cada rol del YAML debe tener su propio fixture:
- `@pytest.fixture def as_standard_user(app)`: Sesión para cliente estándar.
- `@pytest.fixture def as_problem_user(app)`: Sesión para usuario con anomalías de UI/imágenes.
- `@pytest.fixture def as_performance_glitch_user(app)`: Sesión para usuario con latencia simulada.
- `@pytest.fixture def as_error_user(app)`: Sesión para usuario con manejadores de eventos rotos.
- `@pytest.fixture def as_visual_user(app)`: Sesión para usuario con desplazamientos de layout.

Todos los fixtures deben exponerse globalmente en `applications/web/<app>/tests/conftest.py` para permitir su uso directo en tests mediante `@pytest.mark.usefixtures("as_<role>")`.

---

## 7. Protocolo Obligatorio para Operaciones CRUD (Spinners, Loaders y Toasts)
En operaciones que crean, actualizan o eliminan registros (CRUD) dentro de la aplicación, se debe seguir estrictamente la siguiente distribución de responsabilidades por capas:

### 7.1. Auto-Sincronización de Carga en Capa 3 (Loaders & Spinners)
- **PROHIBIDO**: Delegar la espera del spinner o loader al archivo de test (`test_*.py`).
- **OBLIGATORIO**: Todo método compuesto de negocio que envíe un formulario o dispare una mutación asíncrona (ej. `create_customer`, `update_profile`, `delete_item`) **DEBE sincronizarse internamente** antes de retornar `self`:
  - En la Capa 1 se declara el indicador con prefijo `spn_` o `ldr_`: `spn_loading = find_container(css=".spinner-border, .loading-backdrop")`.
  - En la Capa 2 se expone el método atómico: `def wait_for_spinner_to_disappear(self, timeout=15) -> Self: self.spn_loading.wait_disappear(timeout); return self`. Alternativamente se hereda el helper nativo `self.wait_for_loader_to_disappear()`.
  - En la Capa 3, el método compuesto encadena la espera antes del retorno:
    ```python
    def create_record(self, data: dict) -> Self:
        return (
            self.fill_form(data)
                .click_save()
                .wait_for_loader_to_disappear() # Sincronización interna obligatoria
        )
    ```
  - Cuando el método compuesto devuelve el control al archivo de test, la pantalla ya debe estar completamente liberada de overlays y lista para interactuar.

### 7.2. Desacoplamiento de Toasts y Alertas Flotantes
- **PROHIBIDO**: Dispersar selectores duplicados de toasts o alertas en múltiples Page Objects si la aplicación utiliza un sistema de notificaciones unificado del Design System.
- **OBLIGATORIO**: Modelar el contenedor de notificaciones en `applications/web/<app>/components/toast_component.py` (heredando de `BaseComponent`) y exponerlo en el orquestador como `@property def toast(self) -> ToastComponent`, o utilizar los helpers nativos de `BasePage`: `self.get_toast_text(timeout=10)`.

### 7.3. Validación en la Capa de Pruebas (`test_*.py`)
- El archivo de prueba únicamente invoca la acción compuesta de la Capa 3 y compara el mensaje del toast contra el oráculo esperado definido en el JSON (`self.get_expected_for_test()`):
  ```python
  with allure.step("2. Acción: Crear cliente"):
      self.app.customers_page.create_customer(self.test_data)

  with allure.step("3. Verificación: Confirmar notificación Toast de éxito"):
      actual_msg = self.app.toast.get_message()
      expected_msg = self.get_expected_for_test("success_message")
      assert actual_msg == expected_msg, f"Expected toast '{expected_msg}', but got '{actual_msg}'"
  ```

---

## 8. Arquitectura Dual Engine y Reglas de Acciones (`core/ui/actions/`)
El framework soporta ejecución nativa transparente sobre **Selenium WebDriver** y **Microsoft Playwright**:

### 8.1. Estructura Estricta de Acciones
- **PROHIBIDO** crear archivos de acciones sueltos en la raíz de `core/ui/actions/`.
- La carpeta `core/ui/actions/` contiene estrictamente:
  - `contracts/`: Clases abstractas (`ABC`) que definen las firmas universales de los métodos.
  - `selenium/`: Implementaciones nativas exclusivas para Selenium WebDriver (W3C).
  - `playwright/`: Implementaciones nativas exclusivas para Microsoft Playwright (CDP).
  - `factory.py`: `ActionFactory` para resolución dinámica en tiempo de ejecución.
  - `ui_element.py`: Facade que consumen los Page Objects.
- **OBLIGATORIO**: Todo método nuevo añadido a una acción en Selenium DEBE implementarse también en Playwright para mantener **paridad 1:1**.

### 8.2. Prohibición de Importaciones Directas en Tests y Page Objects
- **PROHIBIDO**: Importar `core.ui.actions.selenium.*` o `core.ui.actions.playwright.*` dentro de `pages/` o `tests/`.
- Toda interacción en los Page Objects se realiza exclusivamente a través de los métodos expuestos por el descriptor `find_by` y el facade `UIElement`.

### 8.3. Modo Interactivo y Pantalla de Bienvenida (Splash Screen)
- En modo no-headless (`HEADLESS=false`), `BaseTest` inicializa automáticamente `SplashScreen.show(...)` con una duración por defecto de `3.8s` (configurable vía `SPLASH_DURATION`).
- En Playwright, la ventana se maximiza al 100% mediante `no_viewport=True` y comandos nativos CDP (`Browser.setWindowBounds` con `windowState="maximized"`).

### 8.4. Playwright Trace Viewer Integrado
- En ejecuciones Playwright, `PlaywrightDriverFactory.start_tracing()` se activa automáticamente (`PW_TRACE=true`).
- En la etapa de teardown, `base_test.py` exporta el archivo `reports/traces/{TEST_ID}_trace.zip` y lo adjunta de forma nativa a Allure (`application/zip`) para permitir depuración interactiva con `playwright show-trace`.

---

## 9. Arquitectura de Automatización API (Síncrona y Asíncrona)
- Para pruebas REST API síncronas estándar, se utiliza `core.api.common.base_endpoint.BaseEndpoint`, `RequestBuilder` y `APIResponse`.
- Para suites de alto rendimiento o concurrentes, se utiliza `core.api.async_client.AsyncAPIClient` con soporte para `httpx`, medición automática de latencia (`duration_ms`), aserciones fluidas y adjuntos JSON en Allure.




