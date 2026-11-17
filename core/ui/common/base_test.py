import pytest
import os
from core.ui.common.driver_manager import DriverManager
from core.ui.common.singleton import SingletonMeta
from core.ui.common.base_app import BaseApp
from core.utils.logger_config import (
    setup_logger,
    start_thread_log_capture,
    stop_thread_log_capture,
)
from core.utils.config_manager import ConfigManager
from core.utils.json_loader import JSONLoader
from core.utils.video_recorder import VideoRecorder

class BaseTest(BaseApp):
    """
    Foundational base class for all automated test cases.

    Inherits from `BaseApp` to provide direct access to the shared driver 
    and configuration. It manages the test lifecycle via pytest fixtures 
    and provides utilities for data-driven testing using JSON loaders.

    Attributes:
        persistent_session (bool): If True, the browser session is maintained 
                                   across all test methods in the class.
        app (BaseApp): The application orchestrator for the current project.
        recorder (VideoRecorder): The local screen recorder.
    """
    persistent_session: bool = False
    _shared_driver = None
    
    app: BaseApp = None
    recorder: VideoRecorder = None
    
    @property
    def test_data(self) -> dict:
        """
        Public accessor for the current test's JSON input data (`tests.data`).
        """
        return getattr(self, '_current_test_data', {})

    @property
    def expected_data(self) -> dict:
        """
        Public accessor for the current test's JSON expected results (`tests.expected`).
        """
        return getattr(self, '_current_test_expected', {})
    
    @pytest.fixture(scope="class", autouse=True)
    def _class_driver_cleanup(self):
        """Internal fixture to ensure context-level driver cleanup."""
        yield
        if BaseTest._shared_driver:
            from core.ui.common.base_app import BaseApp
            BaseTest._shared_driver.quit()
            BaseTest._shared_driver = None
            BaseApp.set_driver(None)

    def get_test_data(self, test_id: str = None) -> dict:
        # ... (unchanged) ...
        target_id = test_id if test_id else getattr(self, '_current_test_id', None)
        
        # 1. Yield pre-loaded data if it accurately matches the requested ID
        if hasattr(self, '_current_test_data') and getattr(self, '_current_test_id', None) == target_id:
            if self._current_test_data:
                return self._current_test_data
                
        if not target_id:
            raise ValueError("No Test ID provided and no @test_case decorator found for context.")
            
        # 2. Perform live resolution if cache missed (e.g., loading an external json)
        app_name = getattr(self, 'app_name', 'demo')
        app_type = getattr(self, 'app_type', 'web')
        
        env = os.getenv("ENV")
        if not env:
            env = getattr(self, 'profile', 'qa')
            
        app_path = f"applications/{app_type}/{app_name}"
        
        try:
            from core.utils.json_loader import JSONLoader
            # Attempt Environmental Data Load directly
            env_content = JSONLoader.load_environment_data(app_path, env, target_id)
            if env_content:
                return JSONLoader.get_test_case_data(env_content)
                
            # Fallback to standard data location
            content = JSONLoader.load_test_data(app_path, target_id)
            return JSONLoader.get_test_case_data(content)
        except Exception as e:
            self.logger.warning(f"Could not dynamically resolve test data for {target_id}: {e}")
            return {}

    def get_data_for_test(self, test_id: str = None) -> dict:
        """Alias for get_test_data() to maintain backwards compatibility."""
        return self.get_test_data(test_id)

    def get_test_expected(self, test_id: str = None) -> dict:
        """
        Retrieves the 'expected' oracle dictionary (`tests.expected`) for the current or specified test ID.
        Falls back to `tests.data` if `tests.expected` is empty so legacy JSON files continue working.
        """
        target_id = test_id if test_id else getattr(self, '_current_test_id', None)

        if hasattr(self, '_current_test_expected') and getattr(self, '_current_test_id', None) == target_id:
            if self._current_test_expected:
                return self._current_test_expected

        app_name = getattr(self, 'app_name', 'demo')
        app_type = getattr(self, 'app_type', 'web')
        env = os.getenv("ENV") or getattr(self, 'profile', 'qa')
        app_path = f"applications/{app_type}/{app_name}"

        try:
            from core.utils.json_loader import JSONLoader
            content = JSONLoader.load_environment_data(app_path, env, target_id)
            if not content:
                content = JSONLoader.load_test_data(app_path, target_id)
            if content:
                expected = JSONLoader.get_test_case_expected(content)
                return expected if expected else JSONLoader.get_test_case_data(content)
        except Exception as e:
            self.logger.warning(f"Could not dynamically resolve expected data for {target_id}: {e}")
        return getattr(self, '_current_test_data', {})

    def get_expected_for_test(self, test_id: str = None) -> dict:
        """Alias for get_test_expected() matching get_data_for_test() naming."""
        return self.get_test_expected(test_id)

    def get_bugs_for_test(self) -> list:
        """Returns the list of bug dictionaries (`tests.bugs`) associated with the current test."""
        return getattr(self, '_current_test_bugs', [])

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """
        Automated Setup and Teardown fixture for individual test cases.
        Resolves configuration defaults from decorators or environment variables.
        """
        # Clear Singleton instances (except the driver if persistent)
        SingletonMeta.clear_instances()

        # 1. Resolve Application and Profile
        app_name = getattr(self, 'app_name', 'demo')
        app_type = getattr(self, 'app_type', 'web')
        app_path = f"applications/{app_type}/{app_name}"
        
        # 2. Resolve Environment (Priority: ENV Var > Decorator > Default 'qa')
        env = os.getenv("ENV")
        if not env:
            env = getattr(self, 'profile', 'qa')
        
        # Load configuration
        ConfigManager.load_config(app_path, env)
        
        # 3. Resolve Browser & Engine (Priority: ENV Var > Decorator > Config)
        engine = os.getenv("ENGINE", "selenium").lower()
        browser = os.getenv("BROWSER")
        if not browser:
            browser = getattr(self, 'browser', ConfigManager.get("default.browser", "chrome"))
        
        headless = os.getenv("HEADLESS", "false").lower() == "true"
        
        # --- ROBUST LOG HEADER & DYNAMIC JSON METADATA ---
        func = request.node.function
        test_id = getattr(func, '_test_id', 'N/A')
        json_file_fallback = getattr(func, '_test_json_file', None)
        
        # 4. Load JSON Metadata dynamically here because we finally have Context (App & Env)
        self._current_test_id = test_id
        os.environ["CURRENT_TEST_ID"] = test_id if test_id != 'N/A' else ""
        self._current_test_data = {}
        self._current_test_expected = {}
        self._current_test_bugs = []
        
        # Priority Fallbacks explicitly provided via `@test_case` arguments
        arg_title = getattr(func, '_test_arg_title', None)
        arg_desc = getattr(func, '_test_arg_description', None)
        metadata = {}
        
        try:
            from core.utils.json_loader import JSONLoader
            
            # 1. Try Environment-Specific JSON matching the test ID
            env_content = JSONLoader.load_environment_data(app_path, env, test_id)
            
            # 2. Try Generic Fallback JSON in data/json/{test_id}.json
            if not env_content and (json_file_fallback or test_id != 'N/A'):
                env_content = JSONLoader.load_test_data(app_path, json_file_fallback or test_id)
                
            if env_content:
                metadata = env_content.get("tests", {})
                self._current_test_data = metadata.get("data", {})
                self._current_test_expected = metadata.get("expected", {})
                self._current_test_bugs = metadata.get("bugs", [])
                func._test_metadata = metadata  # Crucial for wrapper to consume Allure tags
                
                # Resolving properties using Priority Queue: JSON -> Args -> Default
                func._test_title = metadata.get("title") or arg_title or func.__name__
                func._test_description = metadata.get("description") or arg_desc or "No description provided."
        except Exception:
            pass

        # Evaluate JSON Execution Control (enabled / allowed environments) before opening browser
        exec_ctrl = metadata.get("execution", {}) if isinstance(metadata, dict) else {}
        if isinstance(exec_ctrl, dict):
            if exec_ctrl.get("enabled", True) is False:
                reason = exec_ctrl.get("skip_reason") or f"Test {test_id} is disabled in JSON execution config."
                pytest.skip(reason)
            allowed_envs = exec_ctrl.get("environments")
            if isinstance(allowed_envs, list) and allowed_envs and env not in allowed_envs:
                pytest.skip(f"Test {test_id} is only enabled for environments {allowed_envs} (active: '{env}').")

        test_title = getattr(func, '_test_title', arg_title or request.node.name)
        test_desc = getattr(func, '_test_description', arg_desc or "No description provided.")
        self._current_test_title = test_title

        # Start isolated thread/test log capture so parallel runs have clean per-test sequences
        start_thread_log_capture(test_id=test_id if test_id != 'N/A' else request.node.name)
        try:
            from core.utils.action_tracer import ActionTracer
            ActionTracer.start_trace(test_id=test_id if test_id != 'N/A' else request.node.name)
        except Exception:
            pass
        
        # Combine test title, context, and name into a single log string so the UI rendering logic
        # visually groups them inside the same .log-header CSS block.
        engine_label = "🎭 Playwright" if engine == "playwright" else "⚡ Selenium"
        header_text = f"🚀 STARTING TEST: {test_id} - {test_title}\nDescription: {test_desc}\nMethod: {func.__name__}\nContext: App={app_name} | Env={env} | Engine={engine_label} | Browser={browser} (Headless: {headless})"
        self.logger.info(header_text)
        
        try:
            # --- WEBDRIVER / PLAYWRIGHT ACQUISITION STRATEGY ---
            if self.persistent_session and BaseTest._shared_driver:
                driver_instance = BaseTest._shared_driver
                self.logger.info("♻️ Reusing persistent browser session for this test.")
            else:
                if engine == "playwright":
                    self.logger.info(f"🎭 Initializing native Playwright session (Browser: {browser}, Headless: {headless})")
                    from core.ui.playwright.driver_factory import PlaywrightDriverFactory
                    from core.ui.playwright.driver_shim import PlaywrightWebDriverShim
                    pw_page = PlaywrightDriverFactory.create_page(browser_name=browser, headless=headless)
                    driver_instance = PlaywrightWebDriverShim(pw_page, browser_name=browser)
                else:
                    self.logger.info(f"⚡ Initializing native Selenium session (Browser: {browser}, Headless: {headless})")
                    driver_instance = DriverManager.get_driver(browser, headless)
                
                try:
                    driver_instance.maximize_window()
                except Exception as e:
                    self.logger.warning(f"Could not maximize window: {e}")
                
                if self.persistent_session:
                    BaseTest._shared_driver = driver_instance
                    self.logger.info("📡 Persistent session enabled. Driver will be shared across the class.")
            
            # Set global driver context
            BaseApp.set_driver(driver_instance)
            
            # Initialize App Orchestrator dynamically based on the app context
            if hasattr(self, 'app_class') and self.app_class:
                self.app = self.app_class()
            else:
                # Dynamic resolution via importlib without static coupling to specific apps
                resolved_app = None
                if app_name:
                    try:
                        import importlib
                        mod_name = f"applications.web.{app_name}.app.{app_name}_app"
                        module = importlib.import_module(mod_name)
                        pascal_name = "".join(part.capitalize() for part in app_name.split("_")) + "App"
                        app_cls = getattr(module, pascal_name, None)
                        if app_cls:
                            resolved_app = app_cls()
                    except (ImportError, AttributeError):
                        pass

                if resolved_app:
                    self.app = resolved_app
                else:
                    from applications.web.demo.app.demo_app import DemoApp
                    self.app = DemoApp()

            # Initialize and start video recording
            self.recorder = VideoRecorder(name=request.node.name, driver=getattr(self, 'driver', None) or driver_instance)
            self.recorder.start()

            # Display Cinematic Engine Splash Screen in non-headless mode
            if not headless:
                try:
                    from core.utils.splash_screen import SplashScreen
                    splash_duration = float(os.getenv("SPLASH_DURATION", "3.8"))
                    SplashScreen.show(
                        driver_instance,
                        engine=engine,
                        browser=browser,
                        env=env,
                        test_id=test_id,
                        test_title=test_title,
                        duration=splash_duration
                    )
                except Exception as e:
                    self.logger.debug(f"Could not display splash screen: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise e
        
        yield
        
        # Cleanup routine
        if self.recorder:
            self.recorder.stop()

        # --- ROBUST LOG FOOTER ---
        if hasattr(self, 'recorder') and self.recorder and getattr(self.recorder, 'video_path', None):
            self.logger.info(f"🎥 Video URL: {self.recorder.video_path}")
            
        self.logger.info(f"🏁 FINISHED TEST: {test_id}")

        # Attach isolated sequential thread log to Allure report
        thread_log = stop_thread_log_capture()
        if thread_log:
            try:
                import allure
                allure.attach(
                    thread_log,
                    name=f"Sequential Execution Log ({test_id})",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except Exception:
                pass

        # Export and attach Time-Travel Action Timeline
        try:
            from core.utils.action_tracer import ActionTracer
            ActionTracer.export_json(test_id)
            timeline_html = ActionTracer.generate_html_timeline(test_id)
            if timeline_html:
                import allure
                allure.attach(
                    timeline_html,
                    name=f"Time-Travel Action Timeline ({test_id})",
                    attachment_type=allure.attachment_type.HTML,
                )
        except Exception:
            pass

        try:
            from core.utils.dynamic_data_resolver import DynamicDataResolver
            DynamicDataResolver.clear_context()
        except Exception:
            pass

        # Export and attach Playwright Trace Viewer archive (.zip)
        if engine == "playwright":
            try:
                from core.ui.playwright.driver_factory import PlaywrightDriverFactory
                trace_dir = os.path.join(os.getcwd(), "reports", "traces")
                trace_path = os.path.join(trace_dir, f"{test_id}_trace.zip")
                saved_trace = PlaywrightDriverFactory.stop_tracing(trace_path)
                if saved_trace and os.path.exists(saved_trace):
                    import allure
                    allure.attach.file(
                        saved_trace,
                        name=f"Playwright Trace Viewer ({test_id})",
                        attachment_type="application/zip",
                        extension="zip"
                    )
                    self.logger.info(f"Attached Playwright trace: {saved_trace}")
            except Exception as e:
                self.logger.debug(f"Failed to export/attach Playwright trace: {e}")

        # --- TERMINATION STRATEGY ---
        if not self.persistent_session:
            self.logger.info("Closing WebDriver session (Isolation mode)")
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                BaseApp.set_driver(None)
        else:
            self.logger.info("Keeping WebDriver session alive (Persistence mode)")
