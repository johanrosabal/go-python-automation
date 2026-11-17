import os
from typing import Any, Optional

class BrowserHUD:
    """
    Injects a non-intrusive, elegant Heads-Up Display (HUD) badge directly into
    the live browser DOM when running non-headless sessions.
    
    Provides immediate visual feedback to the user on screen and in video recordings
    indicating which automation engine (🎭 Playwright or ⚡ Selenium) is driving the browser.
    
    CRITICAL: Uses `pointer-events: none` so it NEVER intercepts clicks or user actions.
    """

    @classmethod
    def is_enabled(cls) -> bool:
        """HUD is enabled whenever headless mode is False."""
        return os.getenv("HEADLESS", "false").lower() != "true"

    @classmethod
    def inject(cls, driver_or_page: Any, engine: Optional[str] = None, test_id: Optional[str] = None):
        """
        Injects or updates the HUD badge in the active browser window.
        """
        if not cls.is_enabled():
            return

        resolved_engine = (engine or os.getenv("ENGINE", "selenium")).lower()
        test_label = test_id or os.getenv("CURRENT_TEST_ID", "")
        
        is_playwright = "playwright" in resolved_engine
        badge_icon = "🎭" if is_playwright else "⚡"
        badge_title = "PLAYWRIGHT" if is_playwright else "SELENIUM"
        badge_bg = "linear-gradient(135deg, rgba(16, 185, 129, 0.92), rgba(5, 150, 105, 0.95))" if is_playwright else "linear-gradient(135deg, rgba(59, 130, 246, 0.92), rgba(30, 64, 175, 0.95))"
        border_color = "rgba(110, 231, 183, 0.5)" if is_playwright else "rgba(147, 197, 253, 0.5)"
        shadow_color = "rgba(16, 185, 129, 0.35)" if is_playwright else "rgba(59, 130, 246, 0.35)"

        test_badge_html = f"<span style='background:rgba(0,0,0,0.3); padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; letter-spacing:0.5px;'>{test_label}</span>" if test_label else ""

        hud_script = f"""
        (function() {{
            try {{
                var hud = document.getElementById('__framework_engine_hud__');
                if (!hud) {{
                    hud = document.createElement('div');
                    hud.id = '__framework_engine_hud__';
                    hud.style.position = 'fixed';
                    hud.style.top = '14px';
                    hud.style.right = '18px';
                    hud.style.zIndex = '2147483647';
                    hud.style.pointerEvents = 'none';
                    hud.style.userSelect = 'none';
                    hud.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
                    hud.style.display = 'flex';
                    hud.style.alignItems = 'center';
                    hud.style.gap = '8px';
                    hud.style.padding = '6px 14px';
                    hud.style.borderRadius = '24px';
                    hud.style.color = '#ffffff';
                    hud.style.fontSize = '12px';
                    hud.style.fontWeight = '700';
                    hud.style.letterSpacing = '0.5px';
                    hud.style.boxShadow = '0 6px 20px {shadow_color}, 0 2px 6px rgba(0,0,0,0.2)';
                    hud.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                    hud.style.backdropFilter = 'blur(10px)';
                    hud.style.webkitBackdropFilter = 'blur(10px)';
                    hud.style.animation = '__hud_slide_down__ 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
                    
                    var styleSheet = document.createElement('style');
                    styleSheet.textContent = `
                        @keyframes __hud_slide_down__ {{
                            from {{ transform: translateY(-25px); opacity: 0; }}
                            to {{ transform: translateY(0); opacity: 1; }}
                        }}
                        @keyframes __hud_pulse__ {{
                            0% {{ transform: scale(0.95); opacity: 0.8; }}
                            50% {{ transform: scale(1.15); opacity: 1; }}
                            100% {{ transform: scale(0.95); opacity: 0.8; }}
                        }}
                    `;
                    document.head.appendChild(styleSheet);
                    document.body.appendChild(hud);
                }}
                
                hud.style.background = '{badge_bg}';
                hud.style.border = '1px solid {border_color}';
                hud.innerHTML = `
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#fff; animation:__hud_pulse__ 1.5s infinite ease-in-out;"></span>
                    <span style="font-size:14px;">{badge_icon}</span>
                    <span>{badge_title}</span>
                    {test_badge_html}
                `;
            }} catch(e) {{}}
        }})();
        """

        try:
            # Handle Playwright Page or Locator
            if hasattr(driver_or_page, "evaluate"):
                driver_or_page.evaluate(hud_script)
            # Handle Selenium WebDriver or PlaywrightWebDriverShim
            elif hasattr(driver_or_page, "execute_script"):
                driver_or_page.execute_script(hud_script)
        except Exception:
            pass

