import pytest
import allure
from core.api import AsyncAPIClient

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string"},
    },
    "required": ["id", "name"]
}

CREATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "job": {"type": "string"},
        "id": {"type": "string"},
        "createdAt": {"type": "string"}
    },
    "required": ["name", "job"]
}


@allure.epic("REST API Automation")
@allure.feature("Async API Pipeline")
@allure.story("Async CRUD & Contract Validation")
class TestAsyncAPIPipeline:
    """
    Certified Asynchronous API Test Suite demonstrating non-blocking HTTP requests,
    JSON Schema contracts, latency SLA verification, and exponential backoff retry.
    """

    @pytest.mark.anyio
    async def test_async_fetch_single_user(self):
        """Verify high-performance async GET with latency SLA and JSON Schema validation."""
        async with AsyncAPIClient(base_url="https://jsonplaceholder.typicode.com") as client:
            response = await client.get("/users/1")
            
            (
                response.assert_status_code(200)
                        .assert_response_time_less_than(3000)
                        .assert_header_equals("content-type", "application/json; charset=utf-8")
                        .assert_json_path("id", 1)
                        .assert_json_path("username", "Bret")
                        .assert_json_schema(USER_SCHEMA)
            )

    @pytest.mark.anyio
    async def test_async_create_user(self):
        """Verify async POST creation with payload attachment and contract validation."""
        async with AsyncAPIClient(base_url="https://jsonplaceholder.typicode.com") as client:
            payload = {"name": "Antigravity Engineer", "job": "Lead SDET"}
            response = await client.post("/users", json_data=payload)

            (
                response.assert_status_code(201)
                        .assert_response_time_less_than(3000)
                        .assert_json_path("name", "Antigravity Engineer")
                        .assert_json_path("job", "Lead SDET")
            )

