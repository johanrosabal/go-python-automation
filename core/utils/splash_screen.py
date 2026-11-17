import os
import time
import urllib.parse
from typing import Any, Optional
from datetime import datetime

class SplashScreen:
    """
    Renders an ultra-modern, AAA Enterprise Splash Screen in the live browser prior
    to navigating to the application under test.
    
    Aesthetic: High-end developer platform (Vercel, Linear, Apple, Stripe Developer).
    Features:
      - Deep obsidian canvas with ambient aurora lighting & radial micro-grid.
      - Glassmorphic aerospace cockpit card with specular border gradient.
      - Authentic high-definition vector emblems for Selenium & Playwright.
      - Live telemetry grid (Environment, Engine, Browser, Reporter).
      - Cyber-luminous progress bar with continuous laser shimmer.
    """

    @classmethod
    def is_enabled(cls) -> bool:
        """Splash screen is rendered exclusively when running in non-headless mode."""
        return os.getenv("HEADLESS", "false").lower() != "true"

    @classmethod
    def generate_html(
        cls,
        engine: str = "selenium",
        browser: str = "chrome",
        env: str = "qa",
        test_id: str = "CT-LOGIN-001",
        test_title: str = "Valid login with standard credentials redirects to Inventory Page"
    ) -> str:
        is_playwright = "playwright" in str(engine).lower()
        now_str = datetime.now().strftime("%H:%M:%S")

        if is_playwright:
            engine_brand = "PLAYWRIGHT"
            engine_sub = "MICROSOFT NATIVE CDP ENGINE"
            engine_tag = "CDP • PROTOCOL v1.40+"
            accent_primary = "#10b981"      # Emerald Neon
            accent_secondary = "#06b6d4"    # Cyan Neon
            accent_glow = "rgba(16, 185, 129, 0.4)"
            accent_bg = "rgba(16, 185, 129, 0.08)"
            accent_border = "rgba(16, 185, 129, 0.3)"
            # Authentic Playwright dual mask / origami emblem
            engine_logo = """
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="12" fill="url(#pw_bg)" stroke="url(#pw_border)" stroke-width="1.5"/>
                <!-- Playwright Theatre Masks Vector -->
                <path d="M14 18C14 14.6863 16.6863 12 20 12C23.3137 12 26 14.6863 26 18V26C26 29.3137 23.3137 32 20 32C16.6863 32 14 29.3137 14 26V18Z" fill="url(#pw_mask1)" fill-opacity="0.9"/>
                <circle cx="18" cy="18" r="1.5" fill="#090d16"/>
                <circle cx="22" cy="18" r="1.5" fill="#090d16"/>
                <path d="M17 24C18 25.5 22 25.5 23 24" stroke="#090d16" stroke-width="1.5" stroke-linecap="round"/>
                
                <path d="M22 20C22 16.6863 24.6863 14 28 14C31.3137 14 34 16.6863 34 20V28C34 31.3137 31.3137 34 28 34C24.6863 34 22 31.3137 22 28V20Z" fill="url(#pw_mask2)" fill-opacity="0.95"/>
                <circle cx="26" cy="20" r="1.5" fill="#090d16"/>
                <circle cx="30" cy="20" r="1.5" fill="#090d16"/>
                <path d="M25 26.5C26 28 30 28 31 26.5" stroke="#090d16" stroke-width="1.5" stroke-linecap="round"/>
                <defs>
                    <linearGradient id="pw_bg" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#064e3b" stop-opacity="0.6"/>
                        <stop stop-color="#022c22" stop-opacity="0.9"/>
                    </linearGradient>
                    <linearGradient id="pw_border" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#34d399"/>
                        <stop stop-color="#059669" stop-opacity="0.3"/>
                    </linearGradient>
                    <linearGradient id="pw_mask1" x1="14" y1="12" x2="26" y2="32" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#38bdf8"/>
                        <stop stop-color="#0284c7"/>
                    </linearGradient>
                    <linearGradient id="pw_mask2" x1="22" y1="14" x2="34" y2="34" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#34d399"/>
                        <stop stop-color="#10b981"/>
                    </linearGradient>
                </defs>
            </svg>
            """
        else:
            engine_brand = "SELENIUM"
            engine_sub = "W3C WEBDRIVER PROTOCOL"
            engine_tag = "W3C • STANDARDS COMPLIANT"
            accent_primary = "#3b82f6"      # Cobalt Blue
            accent_secondary = "#8b5cf6"    # Electric Purple
            accent_glow = "rgba(59, 130, 246, 0.4)"
            accent_bg = "rgba(59, 130, 246, 0.08)"
            accent_border = "rgba(59, 130, 246, 0.3)"
            # Authentic Selenium Periodic Table "Se 34" Vector Emblem
            engine_logo = """
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="12" fill="url(#se_bg)" stroke="url(#se_border)" stroke-width="1.5"/>
                <text x="9" y="15" fill="#93c5fd" font-family="-apple-system, system-ui, sans-serif" font-size="9" font-weight="800">34</text>
                <text x="39" y="15" fill="#60a5fa" font-family="-apple-system, system-ui, sans-serif" font-size="7" font-weight="700" text-anchor="end">78.96</text>
                <text x="24" y="32" fill="#ffffff" font-family="-apple-system, system-ui, sans-serif" font-size="20" font-weight="900" text-anchor="middle" letter-spacing="-1">Se</text>
                <text x="24" y="41" fill="#93c5fd" font-family="-apple-system, system-ui, sans-serif" font-size="6.5" font-weight="800" text-anchor="middle" letter-spacing="1">SELENIUM</text>
                <defs>
                    <linearGradient id="se_bg" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#1e3a8a" stop-opacity="0.8"/>
                        <stop stop-color="#0f172a" stop-opacity="0.95"/>
                    </linearGradient>
                    <linearGradient id="se_border" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#60a5fa"/>
                        <stop stop-color="#2563eb" stop-opacity="0.3"/>
                    </linearGradient>
                </defs>
            </svg>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Dispatch • {test_id}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: #05070c;
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            height: 100vh;
            width: 100vw;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
            -webkit-font-smoothing: antialiased;
        }}

        /* Precision Micro-Grid Background */
        .bg-grid {{
            position: absolute;
            inset: 0;
            background-image: 
                radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(5, 7, 12, 0.2) 0%, #05070c 90%);
            background-size: 32px 32px, 100% 100%;
            pointer-events: none;
        }}

        /* Aurora Lighting */
        .aurora-glow {{
            position: absolute;
            width: 850px;
            height: 480px;
            background: radial-gradient(ellipse at center, {accent_glow} 0%, rgba(5, 7, 12, 0) 70%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            filter: blur(90px);
            opacity: 0.75;
            pointer-events: none;
        }}

        /* Glass Cockpit Container */
        .cockpit-card {{
            position: relative;
            z-index: 10;
            width: 880px;
            max-width: 92vw;
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.85) 0%, rgba(10, 15, 26, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            box-shadow: 
                0 40px 100px -20px rgba(0, 0, 0, 0.9),
                0 0 0 1px rgba(255, 255, 255, 0.06) inset,
                0 0 45px -10px {accent_glow};
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            overflow: hidden;
            opacity: 1; /* Always visible immediately */
        }}

        /* Top Technical Status Ribbon */
        .ribbon {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 28px;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: #94a3b8;
        }}

        .ribbon-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .sentinel-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: {accent_primary};
            box-shadow: 0 0 10px {accent_primary};
            animation: pulse-sentinel 2s infinite ease-in-out;
        }}

        @keyframes pulse-sentinel {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.35); opacity: 0.6; }}
        }}

        .cockpit-content {{
            padding: 36px 40px;
        }}

        /* Hero Engine Identity Banner */
        .hero-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 28px;
        }}

        .hero-left {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .brand-titles {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .meta-subtitle {{
            font-size: 10.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #64748b;
        }}

        .main-engine-title {{
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .engine-badge {{
            display: inline-flex;
            flex-direction: column;
            align-items: flex-end;
            padding: 8px 16px;
            background: {accent_bg};
            border: 1px solid {accent_border};
            border-radius: 10px;
            box-shadow: 0 4px 20px -2px {accent_glow};
        }}

        .engine-badge-brand {{
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: {accent_primary};
        }}

        .engine-badge-sub {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.5px;
            color: #94a3b8;
            font-weight: 600;
        }}

        /* Test Scenario Showcase Box */
        .scenario-panel {{
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 26px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) inset;
        }}

        .scenario-header {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .id-badge {{
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 4px 12px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: 0.5px;
        }}

        .type-badge {{
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #64748b;
        }}

        .scenario-headline {{
            font-size: 17px;
            font-weight: 600;
            line-height: 1.5;
            color: #f8fafc;
        }}

        /* Real-Time Telemetry Matrix */
        .telemetry-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 30px;
        }}

        .telemetry-item {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .telemetry-label {{
            font-size: 9.5px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #64748b;
            font-weight: 700;
        }}

        .telemetry-val {{
            font-size: 13.5px;
            font-weight: 700;
            color: #e2e8f0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Laser Loading Bar & Stream */
        .loading-deck {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .track {{
            height: 5px;
            width: 100%;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }}

        .laser-bar {{
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, 
                transparent 0%, 
                {accent_secondary} 25%, 
                {accent_primary} 50%, 
                #ffffff 75%, 
                transparent 100%);
            background-size: 200% 100%;
            border-radius: 8px;
            animation: laser-slide 1.8s infinite linear;
            box-shadow: 0 0 16px {accent_primary};
        }}

        @keyframes laser-slide {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}

        .console-stream {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #64748b;
        }}

        .console-cmd {{
            color: #94a3b8;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .console-cmd::before {{
            content: "⚡";
            color: {accent_primary};
            font-size: 10px;
        }}

        .console-status {{
            color: {accent_primary};
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="aurora-glow"></div>

    <div class="cockpit-card">
        <!-- Technical Ribbon -->
        <div class="ribbon">
            <div class="ribbon-left">
                <div class="sentinel-dot"></div>
                <span>TEST RUNNER DISPATCH CONTROL</span>
            </div>
            <div>UTC {now_str} • {engine_tag}</div>
        </div>

        <!-- Cockpit Body -->
        <div class="cockpit-content">
            <!-- Brand & Authentic Engine Identity -->
            <div class="hero-banner">
                <div class="hero-left">
                    {engine_logo}
                    <div class="brand-titles">
                        <span class="meta-subtitle">ENTERPRISE AUTOMATION SUITE</span>
                        <h1 class="main-engine-title">{engine_brand} <span style="font-weight:400; color:#64748b; font-size:18px;">ENGINE</span></h1>
                    </div>
                </div>

                <div class="engine-badge">
                    <span class="engine-badge-brand">{engine_brand}</span>
                    <span class="engine-badge-sub">{engine_sub}</span>
                </div>
            </div>

            <!-- Scenario Showcase -->
            <div class="scenario-panel">
                <div class="scenario-header">
                    <span class="id-badge">{test_id}</span>
                    <span class="type-badge">END-TO-END AUTOMATION SCENARIO</span>
                </div>
                <div class="scenario-headline">{test_title}</div>
            </div>

            <!-- Telemetry Matrix -->
            <div class="telemetry-grid">
                <div class="telemetry-item">
                    <span class="telemetry-label">Target Environment</span>
                    <span class="telemetry-val" style="color: {accent_primary};">{env.upper()} GATEWAY</span>
                </div>
                <div class="telemetry-item">
                    <span class="telemetry-label">Browser Client</span>
                    <span class="telemetry-val">{browser.title()} Native</span>
                </div>
                <div class="telemetry-item">
                    <span class="telemetry-label">Execution Mode</span>
                    <span class="telemetry-val">Interactive Desktop</span>
                </div>
                <div class="telemetry-item">
                    <span class="telemetry-label">Telemetry Stream</span>
                    <span class="telemetry-val" style="color: {accent_primary};">Active • Allure</span>
                </div>
            </div>

            <!-- Loading Deck -->
            <div class="loading-deck">
                <div class="track">
                    <div class="laser-bar"></div>
                </div>
                <div class="console-stream">
                    <span class="console-cmd">Initializing browser session & dispatching to target URL...</span>
                    <span class="console-status">ONLINE</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html

    @classmethod
    def get_data_url(cls, **kwargs) -> str:
        """Returns the Splash Screen as a self-contained data: URL."""
        html = cls.generate_html(**kwargs)
        encoded = urllib.parse.quote(html)
        return f"data:text/html;charset=utf-8,{encoded}"

    @classmethod
    def show(
        cls,
        driver_or_page: Any,
        engine: str = "selenium",
        browser: str = "chrome",
        env: str = "qa",
        test_id: str = "N/A",
        test_title: str = "Automated Test Scenario",
        duration: Optional[float] = None
    ):
        """
        Renders the Splash Screen inside the browser for `duration` seconds
        before the test navigates to the target URL.
        """
        if not cls.is_enabled():
            return

        if duration is None:
            duration = float(os.getenv("SPLASH_DURATION", "3.8"))

        splash_url = cls.get_data_url(
            engine=engine,
            browser=browser,
            env=env,
            test_id=test_id,
            test_title=test_title
        )

        try:
            # Playwright Page instance
            if hasattr(driver_or_page, "goto"):
                driver_or_page.goto(splash_url, wait_until="domcontentloaded")
                time.sleep(duration)
            # Selenium WebDriver or PlaywrightWebDriverShim
            elif hasattr(driver_or_page, "get"):
                driver_or_page.get(splash_url)
                time.sleep(duration)
        except Exception:
            pass
