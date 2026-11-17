import asyncio
import time
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import httpx
import allure
from core.utils.logger_config import setup_logger

logger = setup_logger("AsyncAPIClient")


class AsyncAPIResponse:
    """
    Asynchronous API Response wrapper providing fluent assertions,
    timing metrics, JSON schema contract validation, and structured payload extraction.
    """

    def __init__(self, response: httpx.Response, duration_ms: float):
        self._response = response
        self.status_code: int = response.status_code
        self.reason_phrase: str = response.reason_phrase
        self.text: str = response.text
        self.headers: httpx.Headers = response.headers
        self.duration_ms: float = duration_ms

    @property
    def body(self) -> Any:
        """Returns parsed JSON if valid, or raw string otherwise."""
        try:
            return self._response.json()
        except Exception:
            return self.text

    def json(self) -> Any:
        """Explicit JSON parser."""
        return self._response.json()

    def assert_status_code(self, expected_code: int) -> "AsyncAPIResponse":
        """Asserts expected HTTP status code."""
        with allure.step(f"Assert Async HTTP Status is {expected_code}"):
            assert self.status_code == expected_code, (
                f"Expected status {expected_code}, but got {self.status_code}. Response: {self.text}"
            )
        return self

    def assert_status_code_in(self, expected_codes: List[int]) -> "AsyncAPIResponse":
        """Asserts that HTTP status code belongs to a list of allowed codes."""
        with allure.step(f"Assert Async HTTP Status in {expected_codes}"):
            assert self.status_code in expected_codes, (
                f"Expected status in {expected_codes}, but got {self.status_code}. Response: {self.text}"
            )
        return self

    def assert_response_time_less_than(self, max_ms: float) -> "AsyncAPIResponse":
        """Asserts that the asynchronous response was served faster than max_ms SLA."""
        with allure.step(f"Assert Latency < {max_ms}ms"):
            assert self.duration_ms <= max_ms, (
                f"Latency SLA exceeded: took {self.duration_ms:.1f}ms, expected <= {max_ms}ms"
            )
        return self

    def assert_header_equals(self, header: str, expected_value: str) -> "AsyncAPIResponse":
        """Asserts that a specific HTTP response header equals expected value."""
        with allure.step(f"Assert header '{header}' equals '{expected_value}'"):
            actual = self.headers.get(header)
            assert actual == expected_value, (
                f"Expected header '{header}' to be '{expected_value}', but got '{actual}'"
            )
        return self

    def assert_json_schema(self, schema_dict: Dict[str, Any]) -> "AsyncAPIResponse":
        """
        Validates the asynchronous JSON response against a JSON Schema contract.
        """
        with allure.step("Validate JSON Schema contract"):
            try:
                import jsonschema
                data = self._response.json()
                jsonschema.validate(instance=data, schema=schema_dict)
            except Exception as e:
                raise AssertionError(f"JSON Schema contract validation failed: {e}\nPayload: {self.text}")
        return self

    def assert_json_path(self, key: str, expected_value: Any) -> "AsyncAPIResponse":
        """Asserts key value within JSON dictionary."""
        with allure.step(f"Assert JSON path '{key}' equals '{expected_value}'"):
            data = self.body
            if not isinstance(data, dict):
                raise AssertionError(f"Response body is not a JSON dictionary: {self.text}")
            actual_value = data.get(key)
            assert actual_value == expected_value, (
                f"Expected '{key}' to be '{expected_value}', but got '{actual_value}'"
            )
        return self

    def assert_contains(self, text: str) -> "AsyncAPIResponse":
        """Asserts that text appears anywhere in the raw response."""
        with allure.step(f"Assert body contains '{text}'"):
            assert text in self.text, f"Text '{text}' not found in response body"
        return self

    def __repr__(self) -> str:
        return f"<AsyncAPIResponse [{self.status_code}] ({self.duration_ms:.1f}ms)>"


class AsyncAPIClient:
    """
    High-performance Async HTTP Client for REST API Automation.
    Built on top of httpx.AsyncClient with connection pooling, automatic timing,
    automatic retry with exponential backoff, and structured Allure reporting.
    """

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        verify_ssl: bool = False,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504)
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {"Content-Type": "application/json", "Accept": "application/json"}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_status_codes = retry_status_codes
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncAPIClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
        return self._client

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> AsyncAPIResponse:
        """
        Dispatches an async HTTP request with auto-retry on transient errors and measures latency.
        """
        client = self._ensure_client()
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = {**self.headers, **(headers or {})}

        logger.info(f"⚡ [ASYNC {method.upper()}] {url}")
        
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            start_time = time.perf_counter()
            try:
                with allure.step(f"Async HTTP {method.upper()} -> {endpoint} (Attempt {attempt})"):
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        params=params,
                        data=data,
                        json=json_data,
                        headers=merged_headers,
                        **kwargs
                    )
                    duration_ms = (time.perf_counter() - start_time) * 1000

                    # Check if retryable HTTP status
                    if response.status_code in self.retry_status_codes and attempt < self.max_retries:
                        sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                        logger.warning(
                            f"HTTP {response.status_code} on attempt {attempt}/{self.max_retries}. "
                            f"Retrying in {sleep_time:.2f}s..."
                        )
                        await asyncio.sleep(sleep_time)
                        continue

                    # Attach payload and response to Allure step
                    try:
                        if json_data:
                            allure.attach(
                                json.dumps(json_data, indent=2),
                                name="Request JSON Payload",
                                attachment_type=allure.attachment_type.JSON
                            )
                        allure.attach(
                            response.text,
                            name=f"Response ({response.status_code}) [{duration_ms:.1f}ms]",
                            attachment_type=allure.attachment_type.JSON if "json" in response.headers.get("content-type", "") else allure.attachment_type.TEXT
                        )
                    except Exception:
                        pass

                    logger.info(f"⬅ [{response.status_code}] ({duration_ms:.1f}ms)")
                    return AsyncAPIResponse(response, duration_ms)

            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                    logger.warning(
                        f"Transport error '{exc}' on attempt {attempt}/{self.max_retries}. "
                        f"Retrying in {sleep_time:.2f}s..."
                    )
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(f"Failed all {self.max_retries} attempts on {url}: {exc}")
                    raise exc

        if last_exception:
            raise last_exception

    async def get(self, endpoint: str, **kwargs) -> AsyncAPIResponse:
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> AsyncAPIResponse:
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> AsyncAPIResponse:
        return await self.request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> AsyncAPIResponse:
        return await self.request("DELETE", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> AsyncAPIResponse:
        return await self.request("PATCH", endpoint, **kwargs)

    async def close(self):
        """Closes the underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
