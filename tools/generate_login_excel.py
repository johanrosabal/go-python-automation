import os
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Define target output path
output_dir = os.path.abspath("applications/web/demo/data/excel")
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, "saucedemo_login_test_cases.xlsx")

wb = Workbook()

# Define styling
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
sub_header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
sub_header_font = Font(name="Calibri", size=10, bold=True, color="1F4E79")

zebra_even = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
zebra_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

thin_gray = Side(border_style="thin", color="D3D3D3")
cell_border = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)

alignment_top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
alignment_top_center = Alignment(horizontal="center", vertical="top")

# Status styles
tag_pill_styles = {
    "POSITIVE": Font(name="Calibri", size=10, bold=True, color="2E7D32"),
    "NEGATIVE": Font(name="Calibri", size=10, bold=True, color="C62828"),
    "SECURITY": Font(name="Calibri", size=10, bold=True, color="6A1B9A"),
    "UI-UX": Font(name="Calibri", size=10, bold=True, color="0277BD"),
}

columns = [
    ("Test ID", 14),
    ("Epic", 22),
    ("Feature", 24),
    ("Story", 26),
    ("Test Case Title", 38),
    ("Type", 12),
    ("Priority", 10),
    ("Severity", 12),
    ("Preconditions", 30),
    ("Execution Steps", 42),
    ("Test Data (Input JSON)", 34),
    ("Expected Results (Oracle JSON)", 36),
    ("Automation Status", 18),
]

# Complete set of granular test cases divided across 5 core features
test_cases = [
    # Feature 1: Happy Path & Session Lifecycle
    {
        "id": "CT-LOGIN-001",
        "epic": "Identity & Access Management",
        "feature": "Happy Path & Session Lifecycle",
        "story": "Standard User Authentication",
        "title": "Valid login with standard credentials redirects to Inventory Page",
        "type": "POSITIVE",
        "priority": "P1",
        "severity": "Critical",
        "preconditions": "Login page is accessible; standard_user credentials are valid in YAML",
        "steps": "1. Open Login Page\n2. Verify page readiness (is_loaded)\n3. Enter standard_user and password\n4. Click Login button\n5. Verify redirect to inventory.html",
        "data": json.dumps({"role": "standard"}, indent=2),
        "expected": json.dumps({"expected_url_contains": "inventory.html", "inventory_title": "Products"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-002",
        "epic": "Identity & Access Management",
        "feature": "Happy Path & Session Lifecycle",
        "story": "Session Termination",
        "title": "Logout from Inventory returns user to Login Page with reset state",
        "type": "POSITIVE",
        "priority": "P1",
        "severity": "High",
        "preconditions": "User is authenticated and on Inventory Page",
        "steps": "1. Open Sidebar Menu via SidebarComponent\n2. Click Logout link\n3. Verify redirect back to base Login URL\n4. Verify Login button is visible and fields are empty",
        "data": json.dumps({"username": "standard_user", "password": "secret_sauce"}, indent=2),
        "expected": json.dumps({"expected_url_contains": "saucedemo.com", "login_button_visible": True}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-003",
        "epic": "Identity & Access Management",
        "feature": "Happy Path & Session Lifecycle",
        "story": "Dynamic Page Credential Login",
        "title": "Login dynamically using credentials parsed directly from the page footer panel",
        "type": "POSITIVE",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login page footer credentials panel is visible",
        "steps": "1. Read accepted usernames list from footer panel\n2. Read password hint from footer panel\n3. Type first parsed username and password\n4. Click Login\n5. Confirm inventory page is loaded",
        "data": json.dumps({"user_index": 0}, indent=2),
        "expected": json.dumps({"inventory_title": "Products"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },

    # Feature 2: Credential Roles & Account Statuses
    {
        "id": "CT-LOGIN-004",
        "epic": "Identity & Access Management",
        "feature": "Credential Roles & Account Status",
        "story": "Locked Account Handling",
        "title": "Login attempt with locked_out_user displays account locked error message",
        "type": "NEGATIVE",
        "priority": "P1",
        "severity": "Critical",
        "preconditions": "Login page is accessible; locked_out_user role is configured in YAML",
        "steps": "1. Open Login Page\n2. Enter locked_out_user credentials\n3. Click Login button\n4. Verify error banner text matches messages.error_locked\n5. Verify user remains on login page",
        "data": json.dumps({"role": "locked"}, indent=2),
        "expected": json.dumps({"error_key": "messages.error_locked"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-005",
        "epic": "Identity & Access Management",
        "feature": "Credential Roles & Account Status",
        "story": "Degraded Account Assets Handling",
        "title": "Login with problem_user allows access while maintaining UI stability",
        "type": "POSITIVE",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login page is accessible; problem_user role is configured in YAML",
        "steps": "1. Open Login Page\n2. Enter problem_user credentials\n3. Click Login button\n4. Confirm Inventory page loads successfully despite broken media",
        "data": json.dumps({"role": "problem"}, indent=2),
        "expected": json.dumps({"expected_url_contains": "inventory.html"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-006",
        "epic": "Identity & Access Management",
        "feature": "Credential Roles & Account Status",
        "story": "Performance Latency Handling",
        "title": "Login with performance_glitch_user succeeds within acceptable SLA threshold",
        "type": "POSITIVE",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login page is accessible; performance_glitch_user role is configured in YAML",
        "steps": "1. Open Login Page\n2. Enter performance_glitch_user credentials\n3. Click Login button\n4. Wait with explicit fluent timeout for inventory page to load (SLA <= 15s)",
        "data": json.dumps({"role": "performance"}, indent=2),
        "expected": json.dumps({"expected_url_contains": "inventory.html", "max_wait_seconds": 15}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },

    # Feature 3: Negative Scenarios & Missing Fields
    {
        "id": "CT-LOGIN-007",
        "epic": "Identity & Access Management",
        "feature": "Negative Authentication & Missing Fields",
        "story": "Empty Username Validation",
        "title": "Login attempt with empty username and valid password displays username required error",
        "type": "NEGATIVE",
        "priority": "P1",
        "severity": "High",
        "preconditions": "Login page loaded; Username field empty",
        "steps": "1. Open Login Page\n2. Leave username field blank\n3. Type valid password\n4. Click Login button\n5. Verify error banner text is 'Epic sadface: Username is required'",
        "data": json.dumps({"username": "", "password": "secret_sauce"}, indent=2),
        "expected": json.dumps({"error_key": "messages.error_username_required"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-008",
        "epic": "Identity & Access Management",
        "feature": "Negative Authentication & Missing Fields",
        "story": "Empty Password Validation",
        "title": "Login attempt with valid username and empty password displays password required error",
        "type": "NEGATIVE",
        "priority": "P1",
        "severity": "High",
        "preconditions": "Login page loaded; Password field empty",
        "steps": "1. Open Login Page\n2. Type standard_user in username field\n3. Leave password field blank\n4. Click Login button\n5. Verify error banner text is 'Epic sadface: Password is required'",
        "data": json.dumps({"username": "standard_user", "password": ""}, indent=2),
        "expected": json.dumps({"error_key": "messages.error_password_required"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-009",
        "epic": "Identity & Access Management",
        "feature": "Negative Authentication & Missing Fields",
        "story": "Both Fields Empty Validation",
        "title": "Login attempt with both username and password empty prioritizes username required error",
        "type": "NEGATIVE",
        "priority": "P1",
        "severity": "High",
        "preconditions": "Login page loaded; Both fields empty",
        "steps": "1. Open Login Page\n2. Do not enter any text in username or password\n3. Click Login button directly\n4. Verify error banner text is 'Epic sadface: Username is required'",
        "data": json.dumps({"username": "", "password": ""}, indent=2),
        "expected": json.dumps({"error_key": "messages.error_username_required"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-010",
        "epic": "Identity & Access Management",
        "feature": "Negative Authentication & Missing Fields",
        "story": "Invalid Credentials Mismatch",
        "title": "Login attempt with unregistered credentials displays username and password mismatch error",
        "type": "NEGATIVE",
        "priority": "P1",
        "severity": "Critical",
        "preconditions": "Login page loaded; User 'invalid_user' does not exist",
        "steps": "1. Open Login Page\n2. Enter invalid_user in username field\n3. Enter wrong_password in password field\n4. Click Login button\n5. Verify error banner text matches messages.error_invalid",
        "data": json.dumps({"username": "invalid_user", "password": "wrong_password"}, indent=2),
        "expected": json.dumps({"error_key": "messages.error_invalid"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },

    # Feature 4: UI Validation UX & Error Recovery
    {
        "id": "CT-LOGIN-011",
        "epic": "Identity & Access Management",
        "feature": "UI Validation & Error Recovery",
        "story": "Visual Error Feedback & Indicators",
        "title": "Failed login highlights input borders in red and renders SVG error icons",
        "type": "UI-UX",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login page is loaded",
        "steps": "1. Click Login with empty fields to trigger validation failure\n2. Verify input_username has CSS class 'error'\n3. Verify input_password has CSS class 'error'\n4. Verify red circle-xmark SVG icon appears next to username\n5. Verify red circle-xmark SVG icon appears next to password",
        "data": json.dumps({"username": "", "password": ""}, indent=2),
        "expected": json.dumps({
            "username_has_error_class": True,
            "password_has_error_class": True,
            "username_error_icon_visible": True,
            "password_error_icon_visible": True
        }, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-012",
        "epic": "Identity & Access Management",
        "feature": "UI Validation & Error Recovery",
        "story": "Error Dismissal Behavior",
        "title": "Clicking the 'X' dismiss button removes error banner and clears field error classes",
        "type": "UI-UX",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login error banner is currently displayed",
        "steps": "1. Trigger an error banner by attempting login with invalid credentials\n2. Click the 'X' button inside the error banner (btn_dismiss_error)\n3. Verify error banner disappears (wait_disappear)\n4. Verify username and password inputs no longer have the 'error' class",
        "data": json.dumps({"username": "bad_user", "password": "bad_password"}, indent=2),
        "expected": json.dumps({"error_banner_visible": False, "inputs_error_cleared": True}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-013",
        "epic": "Identity & Access Management",
        "feature": "UI Validation & Error Recovery",
        "story": "Form Reset / Clear Fields",
        "title": "Clearing login inputs resets their values to empty without submitting the form",
        "type": "UI-UX",
        "priority": "P3",
        "severity": "Low",
        "preconditions": "Login page is loaded",
        "steps": "1. Type text into username and password fields\n2. Call clear_login_form() method\n3. Verify get_form_values(['username', 'password']) returns empty strings\n4. Verify user remains on login page without error banner",
        "data": json.dumps({"username": "sample_user", "password": "sample_password"}, indent=2),
        "expected": json.dumps({"username": "", "password": "", "error_banner_visible": False}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },

    # Feature 5: Security & Input Masking
    {
        "id": "CT-LOGIN-014",
        "epic": "Identity & Access Management",
        "feature": "Security & Input Masking",
        "story": "Password Masking Attribute",
        "title": "Password input has HTML type='password' to mask characters on screen",
        "type": "SECURITY",
        "priority": "P1",
        "severity": "High",
        "preconditions": "Login page is loaded",
        "steps": "1. Open Login Page\n2. Inspect password input element\n3. Retrieve the 'type' HTML attribute\n4. Assert attribute value equals 'password'",
        "data": json.dumps({}, indent=2),
        "expected": json.dumps({"password_field_type": "password"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
    {
        "id": "CT-LOGIN-015",
        "epic": "Identity & Access Management",
        "feature": "Security & Input Masking",
        "story": "Keyboard Form Submission",
        "title": "Submitting login form by pressing ENTER on password field successfully authenticates",
        "type": "POSITIVE",
        "priority": "P2",
        "severity": "Medium",
        "preconditions": "Login page is loaded",
        "steps": "1. Type standard_user in username field\n2. Type secret_sauce in password field\n3. Press ENTER key on password field (press_enter)\n4. Verify form submits and redirects to Inventory Page",
        "data": json.dumps({"role": "standard"}, indent=2),
        "expected": json.dumps({"expected_url_contains": "inventory.html"}, indent=2),
        "status": "READY_FOR_AUTOMATION",
    },
]

# Sheet 1: Master Test Matrix
ws_matrix = wb.active
ws_matrix.title = "Login Test Cases"
ws_matrix.views.sheetView[0].showGridLines = True

# Write Title Banner
ws_matrix.merge_cells("A1:M1")
title_cell = ws_matrix["A1"]
title_cell.value = "SAUCEDEMO - LOGIN TEST CASES SPECIFICATION MATRIX"
title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
title_cell.fill = PatternFill(start_color="0D233A", end_color="0D233A", fill_type="solid")
title_cell.alignment = Alignment(horizontal="center", vertical="center")
ws_matrix.row_dimensions[1].height = 36

# Write Column Headers in Row 2
for col_idx, (col_name, _) in enumerate(columns, start=1):
    cell = ws_matrix.cell(row=2, column=col_idx, value=col_name)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = cell_border
ws_matrix.row_dimensions[2].height = 28

# Write Data Rows
for row_idx, tc in enumerate(test_cases, start=3):
    fill_to_use = zebra_even if row_idx % 2 == 0 else zebra_odd
    row_values = [
        tc["id"],
        tc["epic"],
        tc["feature"],
        tc["story"],
        tc["title"],
        tc["type"],
        tc["priority"],
        tc["severity"],
        tc["preconditions"],
        tc["steps"],
        tc["data"],
        tc["expected"],
        tc["status"],
    ]
    for col_idx, val in enumerate(row_values, start=1):
        c = ws_matrix.cell(row=row_idx, column=col_idx, value=val)
        c.fill = fill_to_use
        c.border = cell_border
        
        # Center ID, Type, Priority, Severity, Status
        if col_idx in [1, 6, 7, 8, 13]:
            c.alignment = alignment_top_center
        else:
            c.alignment = alignment_top_left
            
        # Font styling for Type
        if col_idx == 6 and val in tag_pill_styles:
            c.font = tag_pill_styles[val]
        elif col_idx == 1:
            c.font = Font(name="Calibri", size=10, bold=True, color="1F4E79")
        else:
            c.font = Font(name="Calibri", size=10)

    ws_matrix.row_dimensions[row_idx].height = 70

# Adjust column widths
for col_idx, (_, width) in enumerate(columns, start=1):
    col_letter = get_column_letter(col_idx)
    ws_matrix.column_dimensions[col_letter].width = width

# Sheet 2: Summary Dashboard by Feature
ws_summary = wb.create_sheet(title="Features Summary")
ws_summary.views.sheetView[0].showGridLines = True

ws_summary.merge_cells("A1:D1")
sum_title = ws_summary["A1"]
sum_title.value = "LOGIN SUITE - FEATURE COVERAGE SUMMARY"
sum_title.font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
sum_title.fill = PatternFill(start_color="0D233A", end_color="0D233A", fill_type="solid")
sum_title.alignment = Alignment(horizontal="center", vertical="center")
ws_summary.row_dimensions[1].height = 32

sum_headers = ["Feature Domain", "Test Case Count", "Scenarios / Test IDs", "Target Test File"]
for col_idx, h in enumerate(sum_headers, start=1):
    c = ws_summary.cell(row=2, column=col_idx, value=h)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = cell_border
ws_summary.row_dimensions[2].height = 24

summary_data = [
    ("Happy Path & Session Lifecycle", 3, "CT-LOGIN-001, CT-LOGIN-002, CT-LOGIN-003", "tests/test_login_happy_path.py"),
    ("Credential Roles & Account Status", 3, "CT-LOGIN-004, CT-LOGIN-005, CT-LOGIN-006", "tests/test_login_roles.py"),
    ("Negative Authentication & Missing Fields", 4, "CT-LOGIN-007, CT-LOGIN-008, CT-LOGIN-009, CT-LOGIN-010", "tests/test_login_negative.py"),
    ("UI Validation & Error Recovery", 3, "CT-LOGIN-011, CT-LOGIN-012, CT-LOGIN-013", "tests/test_login_validation_ux.py"),
    ("Security & Input Masking", 2, "CT-LOGIN-014, CT-LOGIN-015", "tests/test_login_security.py"),
]

for row_idx, (feat, count, ids, file_target) in enumerate(summary_data, start=3):
    fill_to_use = zebra_even if row_idx % 2 == 0 else zebra_odd
    for col_idx, val in enumerate([feat, count, ids, file_target], start=1):
        c = ws_summary.cell(row=row_idx, column=col_idx, value=val)
        c.fill = fill_to_use
        c.border = cell_border
        c.font = Font(name="Calibri", size=10)
        c.alignment = Alignment(horizontal="center" if col_idx == 2 else "left", vertical="center")
    ws_summary.row_dimensions[row_idx].height = 24

# Total row
total_row = len(summary_data) + 3
ws_summary.cell(row=total_row, column=1, value="TOTAL TEST CASES").font = Font(name="Calibri", size=10, bold=True)
ws_summary.cell(row=total_row, column=2, value=len(test_cases)).font = Font(name="Calibri", size=10, bold=True)
ws_summary.cell(row=total_row, column=3, value="15 Scenarios mapped").font = Font(name="Calibri", size=10, italic=True)
ws_summary.cell(row=total_row, column=4, value="5 Focused Test Files").font = Font(name="Calibri", size=10, italic=True)
for col_idx in range(1, 5):
    c = ws_summary.cell(row=total_row, column=col_idx)
    c.fill = sub_header_fill
    c.border = cell_border

ws_summary.column_dimensions["A"].width = 38
ws_summary.column_dimensions["B"].width = 18
ws_summary.column_dimensions["C"].width = 46
ws_summary.column_dimensions["D"].width = 34

wb.save(excel_path)
print(f"Excel test case matrix successfully created at: {excel_path}")

