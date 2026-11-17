"""
Smart Selenium Locator Analyzer Utility.

Analyzes an HTML snippet and generates resilient Selenium locators following:
1. Static ID
2. Static Name
3. Label Semantic Resolution (Progressive Upward Container Traversal)
4. aria-label
5. aria-labelledby
6. data-testid / data-test / data-qa
7. Relative XPath
8. CSS Selector
"""

import sys
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag


DYNAMIC_ID_PATTERNS = [
    re.compile(r"^\d+$"),                     # Pure numbers
    re.compile(r"-\d+$"),                     # e.g. input-123
    re.compile(r"_\d+$"),                     # e.g. field_482
    re.compile(r"^[a-f0-9]{8,}-"),            # GUID-like
    re.compile(r"^ember\d+$", re.I),          # Ember
    re.compile(r"^mat-input-\d+$", re.I),     # Angular Material
    re.compile(r"^:r[0-9a-z]+:", re.I),       # React 18 useId
]


def is_static_id(element_id: str) -> bool:
    """Returns True if the ID appears to be stable and not auto-generated."""
    if not element_id or len(element_id) < 2:
        return False
    for pattern in DYNAMIC_ID_PATTERNS:
        if pattern.search(element_id):
            return False
    return True


def determine_prefix(tag_name: str, input_type: Optional[str] = None) -> str:
    """Maps HTML element type to official framework semantic prefix."""
    if tag_name in ("input", "textarea"):
        if input_type in ("checkbox", "radio"):
            return "chk_" if input_type == "checkbox" else "rdo_"
        if input_type in ("button", "submit", "reset"):
            return "btn_"
        if input_type == "file":
            return "upl_"
        return "input_"
    if tag_name in ("button", "a"):
        return "btn_" if tag_name == "button" else "lnk_"
    if tag_name == "select":
        return "ddl_"
    if tag_name in ("table", "tbody", "thead"):
        return "tbl_"
    if tag_name in ("dialog", "aside"):
        return "mdl_"
    if tag_name in ("h1", "h2", "h3", "h4", "h5", "h6", "span", "p", "label"):
        return "lbl_"
    if tag_name in ("img", "svg"):
        return "img_" if tag_name == "img" else "ico_"
    return "el_"


def analyze_element(soup: BeautifulSoup, tag: Tag) -> Dict[str, Any]:
    """Generates the best locator for a given BeautifulSoup Tag."""
    tag_name = tag.name.lower()
    input_type = tag.get("type", "").lower() if tag_name == "input" else None
    prefix = determine_prefix(tag_name, input_type)

    elem_id = tag.get("id")
    elem_name = tag.get("name")
    elem_aria_label = tag.get("aria-label")
    elem_aria_labelledby = tag.get("aria-labelledby")
    elem_test_id = tag.get("data-testid") or tag.get("data-test") or tag.get("data-qa")

    # 1. Tier 1: Static ID
    if elem_id and is_static_id(elem_id):
        matches = len(soup.find_all(id=elem_id))
        if matches == 1:
            return {
                "tier": 1,
                "strategy": "By.ID",
                "value": elem_id,
                "prefix": prefix,
                "reason": f"Unique static ID '{elem_id}' found without dynamic framework suffixes.",
            }

    # 2. Tier 2: Static Name
    if elem_name:
        matches = len(soup.find_all(attrs={"name": elem_name}))
        if matches == 1:
            return {
                "tier": 2,
                "strategy": "By.NAME",
                "value": elem_name,
                "prefix": prefix,
                "reason": f"Unique static name '{elem_name}' attribute.",
            }

    # 3. Tier 3: Label Semantic Association (For Form Elements)
    if tag_name in ("input", "select", "textarea"):
        # Check label with for attribute
        if elem_id:
            label = soup.find("label", attrs={"for": elem_id})
            if label and label.text.strip():
                label_text = label.text.strip()
                return {
                    "tier": 3,
                    "strategy": "By.XPATH",
                    "value": f"//label[normalize-space()='{label_text}']/ancestor::div[.//{tag_name}][1]//{tag_name}",
                    "prefix": prefix,
                    "label_text": label_text,
                    "reason": f"Associated label '{label_text}' via explicit for='{elem_id}' with resilient container fallback.",
                }

        # Check if nested inside label
        parent_label = tag.find_parent("label")
        if parent_label and parent_label.text.strip():
            label_text = parent_label.text.strip().replace("\n", " ")
            return {
                "tier": 3,
                "strategy": "By.XPATH",
                "value": f"//label[contains(normalize-space(), '{label_text[:30]}')]//{tag_name}",
                "prefix": prefix,
                "label_text": label_text[:30],
                "reason": f"Nested input inside label with text '{label_text[:30]}'.",
            }

        # Check nearest parent container containing a label and this input
        curr_parent = tag.parent
        while curr_parent and curr_parent.name not in ("body", "html", "[document]"):
            label = curr_parent.find("label")
            if label and label.text.strip():
                label_text = label.text.strip().replace("\n", " ")
                inputs_in_parent = curr_parent.find_all(tag_name)
                if len(inputs_in_parent) == 1:
                    return {
                        "tier": 3,
                        "strategy": "By.XPATH",
                        "value": f"//label[normalize-space()='{label_text}']/ancestor::div[.//{tag_name}][1]//{tag_name}",
                        "prefix": prefix,
                        "label_text": label_text,
                        "reason": f"Progressive upward container ascent found unique input under label '{label_text}'.",
                    }
            curr_parent = curr_parent.parent

    # 4. Tier 4: aria-label
    if elem_aria_label:
        matches = len(soup.find_all(attrs={"aria-label": elem_aria_label}))
        if matches == 1:
            return {
                "tier": 4,
                "strategy": "By.CSS_SELECTOR",
                "value": f"{tag_name}[aria-label='{elem_aria_label}']",
                "prefix": prefix,
                "reason": f"Unique accessibility aria-label '{elem_aria_label}'.",
            }

    # 5. Tier 5: aria-labelledby
    if elem_aria_labelledby:
        header_el = soup.find(id=elem_aria_labelledby)
        header_text = header_el.text.strip() if header_el else ""
        return {
            "tier": 5,
            "strategy": "By.XPATH",
            "value": f"//*[@aria-labelledby='{elem_aria_labelledby}']",
            "prefix": prefix,
            "reason": f"Accessibility relationship to element with ID '{elem_aria_labelledby}' ('{header_text}').",
        }

    # 6. Tier 6: data-testid / data-test / data-qa
    if elem_test_id:
        return {
            "tier": 6,
            "strategy": "By.CSS_SELECTOR",
            "value": f"[data-testid='{elem_test_id}']",
            "prefix": prefix,
            "reason": f"Testing attribute '{elem_test_id}' stable across refactorings.",
        }

    # 7. Tier 7: Relative XPath (Text or Attributes)
    text = tag.text.strip()
    if text and len(text) < 50:
        clean_text = text.replace("\n", " ").strip()
        return {
            "tier": 7,
            "strategy": "By.XPATH",
            "value": f"//{tag_name}[normalize-space()='{clean_text}']",
            "prefix": prefix,
            "reason": f"Unique visible normalized text '{clean_text}'.",
        }

    # 8. Tier 8: CSS Selector Fallback
    classes = [c for c in tag.get("class", []) if not any(x in c for x in ["active", "focus", "hover", "css-", "sc-"])]
    if classes:
        cls_selector = "." + ".".join(classes[:2])
        return {
            "tier": 8,
            "strategy": "By.CSS_SELECTOR",
            "value": f"{tag_name}{cls_selector}",
            "prefix": prefix,
            "reason": f"Semantic CSS class fallback '{cls_selector}'.",
        }

    # Ultimate fallback
    return {
        "tier": 8,
        "strategy": "By.XPATH",
        "value": f"//{tag_name}",
        "prefix": prefix,
        "reason": "Warning: Non-unique fallback; provide more HTML context.",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_locator.py '<html_snippet>'")
        sys.exit(1)

    html_input = sys.argv[1]
    soup = BeautifulSoup(html_input, "html.parser")
    elements = soup.find_all(["input", "button", "select", "textarea", "a"])

    print(f"Found {len(elements)} interactive element(s) in snippet:\n")
    for idx, el in enumerate(elements, 1):
        res = analyze_element(soup, el)
        clean_name = el.get("name") or el.get("id") or el.get("aria-label") or el.text.strip() or f"element_{idx}"
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", clean_name).strip("_").lower()
        var_name = f"{res['prefix']}{clean_name}"

        print(f"[{idx}] Target: <{el.name}> | Strategy: {res['strategy']} | Tier {res['tier']}")
        print(f"    Reason: {res['reason']}")
        print(f"    # Standard Class Attribute Descriptor:")
        print(f"    {var_name} = find_by({res['strategy']}, \"{res['value']}\", label=\"{clean_name.replace('_', ' ').title()}\")")
        print(f"    # Method Decorator Format:")
        print(f"    @find_by({res['strategy']}, \"{res['value']}\")\n    {var_name} = None\n")


if __name__ == "__main__":
    main()

