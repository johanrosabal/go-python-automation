"""
Legacy AssertCollector Compatibility Adapter.
Integrates legacy assertions with Allure reporting and modern pytest failure traces.
"""
import pytest
import allure
from core.utils.logger_config import setup_logger

logger = setup_logger("AssertCollector")


class AssertCollector:
    def __init__(self):
        self.errors = []

    def assert_group_equal(self, expected, actual):
        try:
            assert expected == actual, f"[Asserts]: Expected value should be [{expected}] not [{actual}]"
        except AssertionError as e:
            self.errors.append(str(e))

    def assert_group_true(self, condition, message):
        try:
            assert condition, message
        except AssertionError as e:
            self.errors.append(str(e))

    def assert_all(self):
        if self.errors:
            pytest.fail("\n".join(self.errors))

    @staticmethod
    def assert_equal(expected, actual):
        with allure.step(f"Assert Equal: expected='{expected}', actual='{actual}'"):
            assert expected == actual, f"[Asserts]: Expected value should be [{expected}] not [{actual}]"

    @staticmethod
    def assert_equal_message(expected, actual, message, page="", method_name=""):
        error_message = f"Validation: {message} | Expected value [{expected}] | Actual value [{actual}]"
        log_message = f"[{page}][{method_name}] " if page and method_name else ""
        step_title = f"{log_message}Assert: {message}"
        
        with allure.step(f"{step_title} (Expected: '{expected}', Actual: '{actual}')"):
            try:
                assert expected == actual, f"{log_message}[Not Match]: {error_message}"
                logger.info(f"{log_message}[Validation]: {message} | {error_message}")
            except AssertionError as e:
                logger.error(str(e))
                pytest.fail(f"{log_message}[Validation]: {message} | {error_message}")
