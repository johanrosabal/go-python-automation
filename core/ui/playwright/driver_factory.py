import os
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from core.utils.logger_config import setup_logger
from core.utils.config_manager import ConfigManager

logger = setup_logger("PlaywrightDriverFactory")


class PlaywrightDriverFactory:
    """
    Factory class responsible for initializing, configuring, and lifecycle-managing
    Playwright Browser, Context, and Page instances in sync mode.
    """

    _playwright_instance: Optional[Playwright] = None
    _browser_instance: Optional[Browser] = None
    _context_instance: Optional[BrowserContext] = None
    _page_instance: Optional[Page] = None

    @classmethod
    def get_playwright(cls) -> Playwright:
        """Starts or returns the global Playwright manager instance."""
        if cls._playwright_instance is None:
            cls._playwright_instance = sync_playwright().start()
        return cls._playwright_instance

    @classmethod
    def create_page(cls, browser_name: str = "chromium", headless: Optional[bool] = None, **kwargs) -> Page:
        """
        Creates and returns a new Playwright Page configured according to the framework environment.

        Args:
            browser_name (str): 'chromium', 'firefox', or 'webkit'.
            headless (Optional[bool]): Override headless mode. If None, reads from ConfigManager.
            **kwargs: Extra arguments for browser context (e.g. viewport, record_video_dir).

        Returns:
            Page: The initialized Playwright page.
        """
        p = cls.get_playwright()

        if headless is None:
            try:
                headless_cfg = ConfigManager.get("browser.headless", True)
                headless = bool(headless_cfg)
            except Exception:
                headless = True

        browser_type_name = browser_name.lower()
        if "chrome" in browser_type_name:
            browser_type = p.chromium
            kwargs.setdefault("channel", "chrome")
        elif "chromium" in browser_type_name:
            browser_type = p.chromium
        elif "firefox" in browser_type_name:
            browser_type = p.firefox
        elif "webkit" in browser_type_name or "safari" in browser_type_name:
            browser_type = p.webkit
        elif "edge" in browser_type_name:
            browser_type = p.chromium
            kwargs.setdefault("channel", "msedge")
        else:
            browser_type = p.chromium

        launch_args = list(kwargs.get("args", []))
        if "--start-maximized" not in launch_args:
            launch_args.append("--start-maximized")

        launch_kwargs = {
            "headless": headless,
            "args": launch_args
        }
        if "channel" in kwargs:
            launch_kwargs["channel"] = kwargs["channel"]

        logger.info(f"Launching Playwright {browser_name} (Headless: {headless})")
        cls._browser_instance = browser_type.launch(**launch_kwargs)

        # Context settings
        context_args: Dict[str, Any] = {
            "ignore_https_errors": True,
        }

        # In interactive mode, use no_viewport=True to allow the browser window to maximize completely
        if not headless and "viewport" not in kwargs:
            context_args["no_viewport"] = True
        else:
            context_args["viewport"] = kwargs.get("viewport", {"width": 1920, "height": 1080})

        # Video recording if enabled
        record_video_dir = kwargs.get("record_video_dir")
        if record_video_dir:
            os.makedirs(record_video_dir, exist_ok=True)
            context_args["record_video_dir"] = record_video_dir

        cls._context_instance = cls._browser_instance.new_context(**context_args)
        cls._page_instance = cls._context_instance.new_page()

        # In non-headless mode, maximize window via CDP and bring window explicitly to front
        if not headless:
            try:
                session = cls._context_instance.new_cdp_session(cls._page_instance)
                res = session.send("Browser.getWindowForTarget")
                window_id = res.get("windowId")
                if window_id:
                    session.send("Browser.setWindowBounds", {
                        "windowId": window_id,
                        "bounds": {"windowState": "maximized"}
                    })
                    session.detach()
            except Exception:
                pass

            try:
                cls._page_instance.bring_to_front()
            except Exception:
                pass

        # Set default timeout (10 seconds to align with framework standards)
        cls._page_instance.set_default_timeout(10000)

        # Automatically start trace recording if enabled via environment or config
        enable_trace = os.getenv("PW_TRACE", "true").lower() in ("true", "1", "yes")
        if enable_trace:
            cls.start_tracing()

        return cls._page_instance

    @classmethod
    def start_tracing(cls, screenshots: bool = True, snapshots: bool = True, sources: bool = True) -> None:
        """
        Starts Playwright execution tracing on the active context.
        Captures full DOM snapshots, screenshots, and action timelines for time-travel debugging.
        """
        if cls._context_instance:
            try:
                cls._context_instance.tracing.start(
                    screenshots=screenshots,
                    snapshots=snapshots,
                    sources=sources
                )
                logger.info("Playwright execution tracing started.")
            except Exception as e:
                logger.debug(f"Failed to start Playwright tracing: {e}")

    @classmethod
    def stop_tracing(cls, output_path: str) -> Optional[str]:
        """
        Stops Playwright tracing and saves the trace archive (.zip) to the given destination.
        
        Args:
            output_path: Absolute or relative destination zip file path.
            
        Returns:
            Optional[str]: Saved archive path if successful, None otherwise.
        """
        if cls._context_instance:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                cls._context_instance.tracing.stop(path=output_path)
                logger.info(f"Playwright trace saved successfully to: {output_path}")
                return output_path
            except Exception as e:
                logger.debug(f"Failed to stop Playwright tracing: {e}")
        return None

    @classmethod
    def close_all(cls) -> None:
        """Closes page, context, browser, and stops Playwright safely."""
        try:
            if cls._page_instance and not cls._page_instance.is_closed():
                cls._page_instance.close()
        except Exception as e:
            logger.debug(f"Error closing Playwright page: {e}")
        finally:
            cls._page_instance = None

        try:
            if cls._context_instance:
                cls._context_instance.close()
        except Exception as e:
            logger.debug(f"Error closing Playwright context: {e}")
        finally:
            cls._context_instance = None

        try:
            if cls._browser_instance:
                cls._browser_instance.close()
        except Exception as e:
            logger.debug(f"Error closing Playwright browser: {e}")
        finally:
            cls._browser_instance = None

        try:
            if cls._playwright_instance:
                cls._playwright_instance.stop()
        except Exception as e:
            logger.debug(f"Error stopping Playwright instance: {e}")
        finally:
            cls._playwright_instance = None

        logger.info("Playwright session terminated cleanly.")
