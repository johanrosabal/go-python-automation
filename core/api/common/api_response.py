import allure
from typing import Any, Dict, List, Optional
import json

class APIResponse:
    """
    Wrapper for requests.Response to provide fluent assertions,
    JSON Schema contract validation, and simplified data access.
    """
    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code
        self.reason = response.reason
        self.text = response.text
        self.headers = response.headers
        self.elapsed_ms = getattr(response, "elapsed", None).total_seconds() * 1000 if hasattr(response, "elapsed") and response.elapsed else 0.0
        
    @property
    def body(self) -> Any:
        """Returns the JSON body or raw text if not JSON."""
        try:
            return self._response.json()
        except Exception:
            return self.text

    def assert_status_code(self, expected_code: int) -> "APIResponse":
        """Asserts the HTTP status code."""
        with allure.step(f"Assert status code is {expected_code}"):
            assert self.status_code == expected_code, \
                f"Expected status {expected_code}, but got {self.status_code}. Response: {self.text}"
        return self

    def assert_status_code_in(self, expected_codes: List[int]) -> "APIResponse":
        """Asserts that the HTTP status code belongs to a list of allowed codes."""
        with allure.step(f"Assert status code in {expected_codes}"):
            assert self.status_code in expected_codes, \
                f"Expected status in {expected_codes}, but got {self.status_code}. Response: {self.text}"
        return self

    def assert_response_time_less_than(self, max_ms: float) -> "APIResponse":
        """Asserts that the response latency was below max_ms threshold."""
        with allure.step(f"Assert response time < {max_ms}ms"):
            assert self.elapsed_ms <= max_ms, \
                f"Response time SLA exceeded: took {self.elapsed_ms:.1f}ms, expected <= {max_ms}ms"
        return self

    def assert_header_equals(self, header: str, expected_value: str) -> "APIResponse":
        """Asserts that a specific HTTP header equals expected value."""
        with allure.step(f"Assert header '{header}' equals '{expected_value}'"):
            actual = self.headers.get(header)
            assert actual == expected_value, \
                f"Expected header '{header}' to be '{expected_value}', but got '{actual}'"
        return self

    def assert_json_schema(self, schema_dict: Dict[str, Any]) -> "APIResponse":
        """
        Validates the JSON response against a JSON Schema standard.
        """
        with allure.step("Validate JSON Schema contract"):
            try:
                import jsonschema
                data = self._response.json()
                jsonschema.validate(instance=data, schema=schema_dict)
            except Exception as e:
                raise AssertionError(f"JSON Schema contract validation failed: {e}\nPayload: {self.text}")
        return self

    def assert_json_path(self, key: str, expected_value: Any) -> "APIResponse":
        """
        Simple assertion for a key in the JSON body.
        """
        with allure.step(f"Assert JSON path '{key}' equals '{expected_value}'"):
            data = self.body
            if not isinstance(data, dict):
                raise AssertionError(f"Response body is not a JSON object: {self.text}")
            
            actual_value = data.get(key)
            assert actual_value == expected_value, \
                f"Expected '{key}' to be '{expected_value}', but got '{actual_value}'"
        return self

    def assert_contains(self, text: str) -> "APIResponse":
        """Asserts that the response body contains the specified text."""
        with allure.step(f"Assert body contains '{text}'"):
            assert text in self.text, f"Expected text '{text}' not found in response body"
        return self

    def __repr__(self):
        return f"<APIResponse [{self.status_code}] ({self.elapsed_ms:.1f}ms)>"
