---
name: create-test-case
description: >-
  Creates or updates automated Test Suites and Test Cases (test_*.py) following the framework's strict enterprise standards: BaseTest inheritance, application decorator (@demo, @pc_agency_portal), mandatory @test_case(id='<TEST_ID>') linking JSON metadata, self.get_data_for_test() / self.test_data and self.get_expected_for_test() consumption, allure.step structured narrative, explicit synchronization before assertions, descriptive assert error messages, and prohibition of .element() in test files. Use this skill whenever the user asks to write, generate, or update test cases.
---

# Skill: Create Test Case (`test_*.py`) — Enterprise Standards

This skill defines the mandatory rules and structure for creating or updating test suites in `applications/web/<app>/tests/test_<feature>.py`.

---

## 0. Mandatory Architectural Laws for Test Cases

1. **Mandatory `@test_case(id="<TEST_ID>")` on EVERY Test Method**:
   - Every `def test_*(self):` **MUST** have `@test_case(id="<TEST_ID>")` (`from core.utils.decorators import test_case`).
   - The `id` links the test method directly to its JSON file in `data/json/<TEST_ID>.json` (or `data/<env>/<TEST_ID>.json`).
   - The framework automatically injects `title`, `description`, `epic`, `feature`, `story`, `severity`, `priority`, `owner`, `tag`, and `bugs` into Allure without repeating them in Python.
   - Pre-browser execution gate: if `"execution": {"enabled": false}` in the JSON, the framework automatically executes `pytest.skip` before launching the browser.

2. **Mandatory Narrative Steps via `with allure.step(...)`**:
   - Every phase of the test **MUST** be wrapped in a descriptive `with allure.step("...")` block.
   - Structure: `1. Navigation` $\rightarrow$ `2. Action / Input` $\rightarrow$ `3. Synchronization` $\rightarrow$ `4. Assertion / Verification`.

3. **Input Data (`data`) vs. Expected Oracles (`expected`)**:
   - Retrieve input values (`tests.data` from JSON) via:
     ```python
     policy_number = self.test_data.get("policy_number")  # or self.get_data_for_test().get("...")
     ```
   - Retrieve expected values / validation keys (`tests.expected` from JSON) via:
     ```python
     expected = self.get_expected_for_test()  # or self.expected_data
     expected_msg = self.config.get(expected.get("error_key"))
     ```

4. **Strict Prohibition of `.element()` in Tests**:
   - **STRICTLY PROHIBITED**: Calling `self.app.<page>.element(...)` or referencing raw tuples `(By.ID, ...)` inside a test file.
   - All interactions **MUST** call the Page Object's Layer 2 atomic methods (`get_<field>()`, `is_<field>()`, `set_<field>()`, `click_<field>()`) or Layer 3 composite methods.

5. **Explicit Synchronization Before Assertions**:
   - Never assert immediately after clicking a search or submit button.
   - Always call the page's synchronization method (e.g., `wait_for_search_results()`, `wait_until_loaded()`, `wait_disappear()`) before reading values.

6. **Descriptive Assertion Messages**:
   - Every `assert` **MUST** include an explanatory failure message showing what was expected versus what was actually retrieved:
     ```python
     assert actual == expected, f"Expected '{expected}', but got '{actual}'"
     ```

7. **Session Management (`persistent_session`) & Role-Based Preconditions**:
   - **Isolated (Default, `persistent_session = False`)**: Browser opens and closes cleanly (`driver.quit()`) for each test method. Zero risk of session bleed between tests.
   - **Persistent (`persistent_session = True`)**: Used for sequential multi-step flows or authenticated portals where subsequent tests reuse the active browser window.
   - **Role-Based Precondition Fixtures (`as_<role>`)**:
     - For post-login business scenarios (catalog, cart, checkout, profile), **DO NOT** repeat login logic in test steps.
     - Decorate tests with `@pytest.mark.usefixtures("as_<role>")` (e.g. `as_standard_user`, `as_problem_user`).
     - Preconditions are **Session-Aware**: In persistent mode, they automatically preserve and reuse the active session if the role matches, or execute an **Identity Switch** (clearing cookies/storage) if a different role is requested.

---

## 1. Reference Blueprint Implementation

```python
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo
import allure


@demo
class TestPolicySearch(BaseTest):
    """
    Test Suite for Policy Search and Validation workflows.
    """
    persistent_session = True

    @test_case(id="PC-PORTAL-020")
    def test_search_by_policy_number(self):
        """
        Scenario: Search for a policy using the Policy Number and verify result card.
        """
        self.logger.info("Starting policy number search scenario")
        
        # 1. Load inputs (tests.data) and expected oracles (tests.expected) from JSON
        policy_number = self.test_data.get("policy_number")
        expected = self.get_expected_for_test()

        # 2. Step: Navigation & Contract Verification
        with allure.step("1. Navigate to Policy Lookup page"):
            search_page = self.app.policy_lookup_page.open()
            assert search_page.is_loaded(), "Policy Lookup Page failed to load anchor elements"

        # 3. Step: Action (using Layer 2 / Layer 3 methods)
        with allure.step(f"2. Enter policy number '{policy_number}' and trigger search"):
            search_page.set_policy_number(policy_number).click_search()

        # 4. Step: Synchronization (Wait for results / spinner disappearance)
        with allure.step("3. Wait for search results to render"):
            search_page.wait_for_search_results(timeout=30)

        # 5. Step: Reading results via Layer 2 getters (NO .element() calls!)
        with allure.step("4. Retrieve and verify actual search results"):
            actual_policy = search_page.get_displayed_policy_number()
            actual_status = search_page.get_policy_status()

            assert (
                actual_policy == policy_number
            ), f"Expected Policy Number to be '{policy_number}', but got '{actual_policy}'"

            if "status" in expected:
                expected_status = expected.get("status")
                assert (
                    actual_status == expected_status
                ), f"Expected Policy Status to be '{expected_status}', but got '{actual_status}'"

        self.logger.info(f"Successfully verified policy search for: {actual_policy}")

    @test_case(id="PC-PORTAL-023")
    def test_search_form_clear_behavior(self):
        """
        Scenario: Verify form resets cleanly when clicking the Clear button.
        """
        self.logger.info("Starting search form clear verification scenario")
        test_data = self.get_data_for_test()

        with allure.step("1. Open search page"):
            search_page = self.app.policy_lookup_page.open()

        with allure.step("2. Fill multiple search fields"):
            search_page.fill_form(test_data)

        with allure.step("3. Verify values are populated before clearing"):
            current_values = search_page.get_form_values(["policy_number", "insured_name"])
            assert current_values.get("policy_number") == test_data.get("policy_number")

        with allure.step("4. Click Clear button"):
            search_page.click_clear()

        with allure.step("5. Verify all fields are reset and empty"):
            cleared_values = search_page.get_form_values(["policy_number", "insured_name"])
            assert cleared_values.get("policy_number") == "", "Policy number was not cleared"
            assert cleared_values.get("insured_name") == "", "Insured name was not cleared"

        self.logger.info("Search form clear functionality verified successfully.")
```

---

## 2. Checklist for Generating or Reviewing Test Cases

Before completing any test file:
- [ ] Does the class inherit from `BaseTest` and apply the application decorator (`@<app>`)?
- [ ] Does **every single** test method have `@test_case(id="<TEST_ID>")` with a real or scaffolded JSON ID?
- [ ] Are test inputs retrieved via `self.test_data.get("...")` or `self.get_data_for_test()`?
- [ ] Are validation oracles retrieved via `self.get_expected_for_test()` or `self.config.get(...)`?
- [ ] Are the main execution blocks wrapped in `with allure.step("...")`?
- [ ] Are page interactions routed exclusively through `self.app.<page_name>`?
- [ ] Is `self.app.<page>.element(...)` completely absent from the test file?
- [ ] Is there explicit synchronization (`wait_for_*` / `wait_until_loaded`) before assertions?
- [ ] Do all assertions have descriptive failure messages (`f"Expected '{expected}', but got '{actual}'"`)?
- [ ] Are scenario start and success logged using `self.logger.info`?
- [ ] If testing post-login business logic, is the authentication encapsulated in a `@pytest.mark.usefixtures("as_<role>")` fixture?

---

## 3. Session-Aware Preconditions Pattern (RBAC & Multi-Role Testing)

When designing automated test cases that require an authenticated user, **never** repeat the login sequence inside the test method body. Instead, consume a role-based precondition fixture from `fixtures/preconditions.py`.

### 3.1. When to Use
- **Authentication Features** (Login validation, wrong passwords, locked accounts): Test the login form directly inside the test body.
- **Business Features** (Catalog, Cart, Orders, Reports, Administration): Decorate with `@pytest.mark.usefixtures("as_<role>")`.

### 3.2. Architecture: Isolation vs Persistence

```python
# Mode A: Complete Isolation (Default)
@demo
class TestIsolatedFeatures(BaseTest):
    persistent_session = False  # Each test gets a fresh, clean browser window
    
    @test_case(id="CT-INV-001")
    @pytest.mark.usefixtures("as_standard_user")
    def test_catalog_for_standard_user(self):
        # Starts immediately on Inventory with standard_user
        pass

# Mode B: Persistent Class Session (Fast Sequential Workflows)
@demo
class TestSequentialWorkflows(BaseTest):
    persistent_session = True   # Shared browser across tests in this class
    
    @test_case(id="CT-INV-001")
    @pytest.mark.usefixtures("as_standard_user")
    def test_add_to_cart_step_1(self):
        # Logs in as standard_user and adds item
        pass
        
    @test_case(id="CT-INV-002")
    @pytest.mark.usefixtures("as_standard_user")
    def test_verify_cart_badge_step_2(self):
        # Session-Aware: REUSES active session from test 1 without re-logging in!
        pass
        
    @test_case(id="CT-INV-003")
    @pytest.mark.usefixtures("as_problem_user")
    def test_different_role_behavior(self):
        # Session-Aware: Detects role change! Performs IDENTITY SWITCH (clears cookies)
        # and logs in as problem_user cleanly.
        pass
```

### 3.3. Key Benefits
1. **Clean Allure Steps**: Precondition steps appear in their own Allure setup container, leaving the test narrative clean.
2. **Speed & Efficiency**: Avoids repetitive browser relaunches and redundant logins.
3. **Resilience**: If the login UI changes, only `preconditions.py` is updated, preserving all downstream business tests.
