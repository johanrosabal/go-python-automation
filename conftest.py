import os
import json
import pytest
from core.utils.cleaner import Cleaner
from core.utils.failure_analyzer import FailureAnalyzer
from core.utils.summary_reporter import SummaryReporter


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook that intercepts test outcomes and triggers the intelligent FailureAnalyzer
    whenever an assertion fails, an element is not found, or an exception occurs.
    Also feeds the SummaryReporter for final tabular reporting.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Record outcome in SummaryReporter
    try:
        SummaryReporter.record_test_result(item, call, rep)
    except Exception:
        pass

    # Only analyze when a failure actually happens (during call or setup)
    if rep.failed and rep.when in ("call", "setup"):
        test_instance = getattr(item, "instance", None)
        driver = getattr(test_instance, "driver", None) if test_instance else None

        # 1. Classify failure and generate root-cause diagnostics
        diagnostic = FailureAnalyzer.analyze(
            exc_info=call.excinfo,
            test_instance=test_instance,
            item=item,
            driver=driver,
        )

        # 2. Capture screenshot on failure if WebDriver is active
        screenshot_path = None
        if driver:
            try:
                screenshots_dir = os.path.join("reports", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                test_slug = (diagnostic.test_id if diagnostic.test_id != "N/A" else item.name).replace(" ", "_")
                filename = f"failure_{test_slug}.png"
                screenshot_path = os.path.join(screenshots_dir, filename)
                driver.save_screenshot(screenshot_path)
                diagnostic.screenshot_path = screenshot_path
            except Exception:
                pass

        # 3. Log ASCII diagnostic card into sequential logger & console
        ascii_card = diagnostic.render_ascii_card()
        logger = getattr(test_instance, "logger", None)
        if logger:
            logger.error("\n" + ascii_card)
        else:
            print("\n" + ascii_card)

        # 4. Attach rich HTML Card and Screenshot to Allure Report
        try:
            import allure
            allure.attach(
                diagnostic.render_html_card(),
                name="🎯 Diagnóstico de Causa Raíz (Failure Analysis)",
                attachment_type=allure.attachment_type.HTML,
            )
            if screenshot_path and os.path.exists(screenshot_path):
                allure.attach.file(
                    screenshot_path,
                    name=f"Failure Screenshot ({diagnostic.test_id})",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception:
            pass

        # 5. Save structured JSON for Web Test Runner, CI and reporting portals
        try:
            diag_dir = os.path.join("reports", "diagnostics")
            os.makedirs(diag_dir, exist_ok=True)
            test_slug = (diagnostic.test_id if diagnostic.test_id != "N/A" else item.name).replace(" ", "_")
            diag_file = os.path.join(diag_dir, f"{test_slug}_diagnostic.json")
            with open(diag_file, "w", encoding="utf-8") as f:
                json.dump(diagnostic.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def pytest_sessionstart(session):
    """
    Hooks into the start of the pytest session.
    """
    SummaryReporter.reset()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Hooks into the final terminal report output to print the enterprise results table.
    """
    table = SummaryReporter.render_table()
    if table:
        terminalreporter.write_line(table)


def pytest_sessionfinish(session, exitstatus):
    """
    Hooks into the end of the pytest session to send notifications.
    """
    from core.utils.notifier import Notifier
    from core.utils.config_manager import ConfigManager
    
    # Get statistics from the session
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    passed = len(reporter.stats.get("passed", [])) if reporter else 0
    failed = len(reporter.stats.get("failed", [])) if reporter else 0
    xfailed = len(reporter.stats.get("xfailed", [])) if reporter else 0
    skipped = len(reporter.stats.get("skipped", [])) if reporter else 0
    total = passed + failed + xfailed + skipped
    
    try:
        project_name = ConfigManager.get("metadata.project_name", "QA Automation")
    except ValueError:
        project_name = "QA Automation"
    
    notifier = Notifier()
    notifier.send_summary(
        project_name=project_name,
        total=total,
        passed=passed,
        failed=failed
    )
