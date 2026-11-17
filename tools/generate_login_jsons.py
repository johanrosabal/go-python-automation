import os
import json
import openpyxl

# Load test cases directly from the generated Excel workbook to guarantee 100% congruency
excel_path = os.path.abspath("applications/web/demo/data/excel/saucedemo_login_test_cases.xlsx")
json_output_dir = os.path.abspath("applications/web/demo/data/json")
os.makedirs(json_output_dir, exist_ok=True)

wb = openpyxl.load_workbook(excel_path)
ws = wb["Login Test Cases"]

# Mapping of method names for testCaseName
test_name_map = {
    "CT-LOGIN-001": "test_valid_login_standard_user",
    "CT-LOGIN-002": "test_logout_returns_to_login_page",
    "CT-LOGIN-003": "test_dynamic_credentials_from_footer",
    "CT-LOGIN-004": "test_locked_out_user_error",
    "CT-LOGIN-005": "test_problem_user_login",
    "CT-LOGIN-006": "test_performance_glitch_user_login",
    "CT-LOGIN-007": "test_login_empty_username",
    "CT-LOGIN-008": "test_login_empty_password",
    "CT-LOGIN-009": "test_login_both_fields_empty",
    "CT-LOGIN-010": "test_login_unregistered_credentials",
    "CT-LOGIN-011": "test_login_error_visual_feedback",
    "CT-LOGIN-012": "test_dismiss_error_banner",
    "CT-LOGIN-013": "test_clear_login_form_inputs",
    "CT-LOGIN-014": "test_password_input_is_masked",
    "CT-LOGIN-015": "test_login_submit_via_enter_key",
}

tag_map = {
    "CT-LOGIN-001": ["LOGIN", "SMOKE", "POSITIVE", "HAPPY_PATH"],
    "CT-LOGIN-002": ["LOGIN", "LOGOUT", "POSITIVE", "SESSION"],
    "CT-LOGIN-003": ["LOGIN", "DYNAMIC", "POSITIVE"],
    "CT-LOGIN-004": ["LOGIN", "NEGATIVE", "ROLES", "LOCKED_USER"],
    "CT-LOGIN-005": ["LOGIN", "ROLES", "PROBLEM_USER", "POSITIVE"],
    "CT-LOGIN-006": ["LOGIN", "ROLES", "PERFORMANCE", "POSITIVE"],
    "CT-LOGIN-007": ["LOGIN", "NEGATIVE", "VALIDATION"],
    "CT-LOGIN-008": ["LOGIN", "NEGATIVE", "VALIDATION"],
    "CT-LOGIN-009": ["LOGIN", "NEGATIVE", "VALIDATION"],
    "CT-LOGIN-010": ["LOGIN", "NEGATIVE", "INVALID_CREDENTIALS"],
    "CT-LOGIN-011": ["LOGIN", "UI_UX", "ERROR_FEEDBACK"],
    "CT-LOGIN-012": ["LOGIN", "UI_UX", "DISMISS"],
    "CT-LOGIN-013": ["LOGIN", "UI_UX", "FORM_RESET"],
    "CT-LOGIN-014": ["LOGIN", "SECURITY", "MASKING"],
    "CT-LOGIN-015": ["LOGIN", "KEYBOARD", "ENTER_KEY", "POSITIVE"],
}

# Row 1 is Title, Row 2 is Header, Rows 3-17 are Test Cases
generated_files = []
for row in range(3, ws.max_row + 1):
    test_id = ws.cell(row=row, column=1).value
    if not test_id:
        continue
    
    epic = ws.cell(row=row, column=2).value
    feature = ws.cell(row=row, column=3).value
    story = ws.cell(row=row, column=4).value
    title = ws.cell(row=row, column=5).value
    tc_type = ws.cell(row=row, column=6).value
    priority = ws.cell(row=row, column=7).value
    severity = ws.cell(row=row, column=8).value
    preconditions_raw = ws.cell(row=row, column=9).value or ""
    steps_raw = ws.cell(row=row, column=10).value or ""
    data_raw = ws.cell(row=row, column=11).value or "{}"
    expected_raw = ws.cell(row=row, column=12).value or "{}"

    # Parse preconditions into list
    preconditions = [p.strip() for p in preconditions_raw.split(";") if p.strip()]
    if not preconditions:
        preconditions = ["Application login page is accessible"]

    # Parse JSON data and expected
    try:
        data_obj = json.loads(data_raw)
    except Exception:
        data_obj = {}

    try:
        expected_obj = json.loads(expected_raw)
    except Exception:
        expected_obj = {}

    # Build description from steps or title
    description = f"{title}. Verifies expected behavior against SauceDemo authentication service."

    test_case_name = test_name_map.get(test_id, f"test_{test_id.lower().replace('-', '_')}")
    tags = tag_map.get(test_id, ["LOGIN", tc_type])

    # Construct the JSON 360 schema
    json_content = {
        "tests": {
            "id": test_id,
            "testCaseName": test_case_name,
            "title": title,
            "description": description,
            "owner": "qa-team",
            "epic": epic,
            "feature": feature,
            "story": story,
            "severity": severity,
            "priority": priority,
            "tag": tags,
            "execution": {
                "enabled": True,
                "environments": ["dev", "qa", "uat", "prod"],
                "skip_reason": ""
            },
            "preconditions": preconditions,
            "link": {
                "url": "https://www.saucedemo.com",
                "name": "SauceDemo Login"
            },
            "bugs": [],
            "data": data_obj,
            "expected": expected_obj
        }
    }

    target_file = os.path.join(json_output_dir, f"{test_id}.json")
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=4, ensure_ascii=False)
    
    generated_files.append(f"{test_id}.json")

print(f"Successfully generated {len(generated_files)} JSON test data files in: {json_output_dir}")
for f in generated_files:
    print(f" - {f}")

