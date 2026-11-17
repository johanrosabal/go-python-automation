---
name: create-test-json
description: >-
  Creates or updates Test Case JSON data files following the framework's 360-degree JSON schema (root 'tests' object with metadata, 'execution', 'preconditions', 'link', 'bugs', 'data' for inputs, and 'expected' for validation oracles). Use this skill whenever the user asks to create or update a JSON data file for a Web UI or API test case.
---

# Skill: Create Test Case JSON (360° Standard)

Follow these rules whenever creating or modifying a test data JSON file:

## Step 1: Determine File Location & Naming
- **File Name**: Must match the Test Case ID used in `@test_case(id="<TEST_ID>")` (e.g., `CT-LOGIN-001.json`).
- **Location**:
  - Standard application-wide JSON: `applications/<web_or_api>/<app_name>/data/json/<TEST_ID>.json`
  - Environment-specific JSON (when data varies per environment): `applications/<web_or_api>/<app_name>/data/<env>/<TEST_ID>.json`

## Step 2: Enforce the Mandatory `"tests"` Root Structure
Never place `"data"` or `"expected"` at the root of the JSON. Always wrap the entire test definition inside `"tests"` and strictly separate `"data"` (inputs) from `"expected"` (validation oracles):

```json
{
    "tests": {
        "id": "CT-LOGIN-001",
        "testCaseName": "test_invalid_login",
        "title": "Invalid Login Attempt",
        "description": "Verify that the system displays an error message when providing invalid credentials.",
        "owner": "qa-team",
        "epic": "Identity & Access Management",
        "feature": "Authentication",
        "story": "User Login Validation",
        "severity": "High",
        "priority": "P1",
        "tag": [
            "LOGIN",
            "NEGATIVE"
        ],
        "execution": {
            "enabled": true,
            "environments": ["dev", "qa", "uat", "prod"],
            "skip_reason": ""
        },
        "preconditions": [
            "Application login page is accessible",
            "User 'invalid_user' is not registered"
        ],
        "link": {
            "url": "https://www.saucedemo.com",
            "name": "SauceDemo"
        },
        "bugs": [
            {
                "id": "BUG-101",
                "title": "Example open defect linked to Allure report",
                "status": "OPEN",
                "url": "https://jira.example.com/browse/BUG-101"
            }
        ],
        "data": {
            "username": "invalid_user",
            "password": "wrong_password"
        },
        "expected": {
            "error_key": "messages.error_invalid"
        }
    }
}
```

## Step 3: Key Alignment with Page Object `fill_form`
- When naming keys inside `"data"`, align them with the Page Object's Layer-2 atomic method suffixes (e.g., if the Page Object has `set_username()` and `set_password()`, name the JSON keys `"username"` and `"password"`). That way `page.fill_form(self.get_data_for_test())` works automatically without extra mapping code.
- If there are no known bugs for the test case, set `"bugs": []`.

