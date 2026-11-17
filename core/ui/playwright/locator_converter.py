from typing import Union, Tuple, Any
from selenium.webdriver.common.by import By


def convert_selenium_locator_to_playwright(locator: Union[Tuple[str, str], str]) -> str:
    """
    Translates Selenium locators (e.g., (By.ID, 'user-name') or (By.XPATH, '//input'))
    into resilient, native Playwright selector strings.

    Args:
        locator (Union[Tuple[str, str], str]): Selenium tuple locator or direct selector.

    Returns:
        str: Playwright-compatible selector string.
    """
    if isinstance(locator, str):
        return locator

    if not isinstance(locator, (tuple, list)) or len(locator) != 2:
        return str(locator)

    by_type, value = locator

    # Normalize By type
    by_lower = str(by_type).lower()

    if by_type == By.ID or by_lower in ("id", "by.id"):
        clean_id = value.lstrip("#")
        return f"id={clean_id}"

    elif by_type == By.XPATH or "xpath" in by_lower:
        return f"xpath={value}"

    elif by_type == By.CSS_SELECTOR or "css" in by_lower:
        return value

    elif by_type == By.CLASS_NAME or "class" in by_lower:
        clean_class = value.lstrip(".")
        return f".{clean_class}"

    elif by_type == By.NAME or by_lower in ("name", "by.name"):
        return f"[name='{value}']"

    elif by_type == By.TAG_NAME or "tag" in by_lower:
        return value

    elif by_type in (By.LINK_TEXT, By.PARTIAL_LINK_TEXT) or "link" in by_lower:
        return f"text={value}"

    # Default fallback
    return value
