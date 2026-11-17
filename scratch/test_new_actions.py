import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from core.ui.actions.selenium import (
    CookieActions,
    StorageActions,
    ScriptActions,
    DiagnosticsActions,
)


def test_new_actions_suite():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    
    # Enable browser logging
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    
    driver = webdriver.Chrome(options=opts)
    try:
        # Navigate to a base page
        driver.get("https://www.saucedemo.com")
        
        # 1. Test CookieActions
        cookies = CookieActions(driver)
        cookies.add(name="custom_auth_token", value="test_jwt_12345", path="/")
        assert cookies.has("custom_auth_token") is True
        assert cookies.get_value("custom_auth_token") == "test_jwt_12345"
        cookies.delete("custom_auth_token")
        assert cookies.has("custom_auth_token") is False
        print("✓ CookieActions test passed")

        # 2. Test StorageActions
        storage = StorageActions(driver)
        # LocalStorage
        storage.local.set("user_cart", {"items": [1, 2, 3], "total": 99.9})
        cart_data = storage.local.get_json("user_cart")
        assert isinstance(cart_data, dict)
        assert cart_data["total"] == 99.9
        assert storage.local.has("user_cart") is True
        storage.local.remove("user_cart")
        assert storage.local.has("user_cart") is False
        
        # SessionStorage
        storage.session.set("session_flag", "active")
        assert storage.session.get("session_flag") == "active"
        storage.session.clear()
        assert storage.session.has("session_flag") is False
        print("✓ StorageActions test passed")

        # 3. Test ScriptActions
        script = ScriptActions(driver)
        assert script.get_document_ready_state() == "complete"
        title_via_js = script.execute("return document.title;")
        assert "Swag Labs" in str(title_via_js)
        
        # Promise evaluation
        res = script.eval_promise("new Promise((resolve) => setTimeout(() => resolve('promise_ok'), 50))")
        assert res == "promise_ok"
        print("✓ ScriptActions test passed")

        # 4. Test DiagnosticsActions
        diagnostics = DiagnosticsActions(driver)
        # Should not raise on saucedemo initial landing
        diagnostics.assert_no_severe_errors()
        print("✓ DiagnosticsActions test passed")

        print("\nALL 4 NEW ACTION CLASSES TESTED & VERIFIED SUCCESSFULLY!")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_new_actions_suite()

