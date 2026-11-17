import json
import allure
from core.utils.logger_config import setup_logger
from requests import Session

class BaseAPIAction:
    """
    Base class for all API action components (GET, POST, etc.).
    Provides shared logging and session management.
    """
    def __init__(self, session: Session):
        self.session = session
        self._logger = None

    @property
    def logger(self):
        if not self._logger:
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger

    def builder(self, method=None):
        """Returns a fluent RequestBuilder for this action."""
        from core.api.common.request_builder import RequestBuilder
        # Infer method from class name if not provided (e.g., GETActions -> GET)
        if not method:
            method = self.__class__.__name__.replace("Actions", "").replace("Action", "").upper()
        return RequestBuilder(self.session, method, self)

    # --- Fluent Builder Shortcuts (Legacy Style Compatibility) ---
    
    def set_url(self, url):
        return self.builder().set_url(url)

    def set_endpoint(self, endpoint):
        return self.builder().set_endpoint(endpoint)

    def set_json(self, json_data):
        return self.builder().set_json(json_data)

    def set_data(self, data):
        return self.builder().set_data(data)

    def set_params(self, params):
        return self.builder().set_params(params)

    def set_auth(self, username, password):
        return self.builder().set_auth(username, password)

    def add_header(self, key, value):
        return self.builder().add_header(key, value)

    def set_files(self, files):
        return self.builder().set_files(files)

    def set_timeout(self, timeout):
        return self.builder().set_timeout(timeout)

    def set_verify(self, verify):
        return self.builder().set_verify(verify)

    def set_allow_redirects(self, allow):
        return self.builder().set_allow_redirects(allow)

    def set_cookies(self, cookies):
        return self.builder().set_cookies(cookies)

    def set_proxies(self, proxies):
        return self.builder().set_proxies(proxies)

    def set_stream(self, stream):
        return self.builder().set_stream(stream)

    def set_cert(self, cert):
        return self.builder().set_cert(cert)

    def build_url(self, **kwargs):
        return self.builder().build_url(**kwargs)

    def _sanitize_headers(self, headers: dict) -> dict:
        """Sanitizes sensitive or overly verbose headers for terminal logging."""
        if not headers:
            return {}
        sanitized = {}
        for k, v in headers.items():
            key_lower = k.lower()
            str_v = str(v)
            if key_lower == "authorization":
                if str_v.startswith("Bearer "):
                    sanitized[k] = f"Bearer {str_v[7:17]}...[TRUNCATED]"
                else:
                    sanitized[k] = f"{str_v[:10]}...[TRUNCATED]"
            elif any(s in key_lower for s in ["subscription-key", "secret", "api-key"]):
                sanitized[k] = f"{str_v[:6]}...[MASKED]"
            elif len(str_v) > 80:
                sanitized[k] = f"{str_v[:80]}...[TRUNCATED]"
            else:
                sanitized[k] = v
        return sanitized

    def _log_request(self, method, url, **kwargs):
        """Logs the request details to the console (sanitized) and Allure (full)."""
        self.logger.info(f"🌐 {method} request to: {url}")
        
        if kwargs.get('json'):
            self.logger.info(f"📦 Body: {json.dumps(kwargs.get('json'))}")
        elif kwargs.get('data'):
            # If data is a dict (Form), log as JSON-like, else as raw string
            data = kwargs.get('data')
            if isinstance(data, dict):
                self.logger.info(f"📦 Form Data: {json.dumps(data)}")
            else:
                self.logger.info(f"📦 Raw Body: {str(data)[:1000]}")
        
        if kwargs.get('files'):
            file_names = [f"{k}: {getattr(v, 'name', 'binary')}" for k, v in kwargs.get('files').items()]
            self.logger.info(f"📁 Files: {', '.join(file_names)}")
            
        if kwargs.get('params'):
            self.logger.info(f"🔍 Params: {json.dumps(kwargs.get('params'))}")
        
        # Log clean sanitized headers to console
        raw_headers = kwargs.get('headers')
        if raw_headers:
            clean_headers = self._sanitize_headers(raw_headers)
            self.logger.info(f"📋 Request Headers: {json.dumps(clean_headers)}")

        # Log clean CURL to console
        curl_cmd_clean = self._to_curl(method, url, mask_sensitive=True, **kwargs)
        self.logger.info(f"💻 CURL: {curl_cmd_clean}")

        # Allure Attachments
        body_data = kwargs.get('json') or kwargs.get('data')
        if body_data:
            if isinstance(body_data, (dict, list)):
                allure.attach(
                    json.dumps(body_data, indent=2),
                    name=f"📦 Request Body ({method})",
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    str(body_data),
                    name=f"📦 Request Body ({method})",
                    attachment_type=allure.attachment_type.TEXT
                )

        curl_cmd_full = self._to_curl(method, url, mask_sensitive=False, **kwargs)
        allure.attach(
            f"Method: {method}\nURL: {url}\nHeaders: {json.dumps(kwargs.get('headers') or {}, indent=2)}\nParams: {json.dumps(kwargs.get('params') or {}, indent=2)}\n\nCURL:\n{curl_cmd_full}",
            name=f"🌐 Request Info: {method} {url}",
            attachment_type=allure.attachment_type.TEXT
        )

    def _log_response(self, response):
        """Logs the response details."""
        status_icon = "✅" if response.status_code < 400 else "❌"
        content_type = response.headers.get("Content-Type", "unknown")
        content_length = len(response.content) if response.content else 0
        self.logger.info(f"{status_icon} Status: {response.status_code} {response.reason} | {content_type} ({content_length} bytes)")

        try:
            body = response.json()
            # If body is a token response, mask the token in terminal log
            if isinstance(body, dict) and "access_token" in body:
                masked_body = dict(body)
                token_str = str(masked_body["access_token"])
                masked_body["access_token"] = f"{token_str[:15]}...[TRUNCATED]"
                self.logger.info(f"📥 Response Body: {json.dumps(masked_body)}")
            else:
                body_str = json.dumps(body)
                if len(body_str) > 1500:
                    self.logger.info(f"📥 Response Body: {body_str[:1500]}... [TRUNCATED]")
                else:
                    self.logger.info(f"📥 Response Body: {body_str}")
            
            # Response Headers kept at DEBUG level to avoid console noise
            self.logger.debug(f"📋 Response Headers: {json.dumps(dict(response.headers))}")
            
            # Allure attachment (pretty printed JSON with status code in name)
            allure.attach(
                json.dumps(body, indent=2),
                name=f"📥 Response Body [{response.status_code} {response.reason}]",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.debug(f"JSON parsing failed or not applicable: {str(e)}")
            text_preview = response.text or ""
            if len(text_preview) > 1500:
                self.logger.info(f"📥 Response Body: {text_preview[:1500]}... [TRUNCATED]")
            else:
                self.logger.info(f"📥 Response Body: {text_preview}")
            
            self.logger.debug(f"📋 Response Headers: {json.dumps(dict(response.headers))}")
            
            allure.attach(
                text_preview,
                name=f"📥 Response Body [{response.status_code} {response.reason}]",
                attachment_type=allure.attachment_type.TEXT
            )


    def _to_curl(self, method, url, mask_sensitive: bool = False, **kwargs):
        """Generates a curl command equivalent to the request."""
        parts = [f"curl -X {method} '{url}'"]
        
        headers = kwargs.get('headers') or {}
        if mask_sensitive:
            headers = self._sanitize_headers(headers) or {}

        for k, v in headers.items():
            parts.append(f"-H '{k}: {v}'")
            
        params = kwargs.get('params')
        if params:
            import urllib.parse
            query = urllib.parse.urlencode(params)
            # Replace the URL in the first part if it doesn't already have params
            if '?' not in parts[0]:
                parts[0] = parts[0].replace(f"'{url}'", f"'{url}?{query}'")
            else:
                parts[0] = parts[0].replace(f"'{url}'", f"'{url}&{query}'")

        json_data = kwargs.get('json')
        if json_data:
            parts.append(f"-d '{json.dumps(json_data)}'")
            
        data = kwargs.get('data')
        if data:
            if isinstance(data, dict):
                parts.append(f"-d '{json.dumps(data)}'")
            else:
                parts.append(f"-d '{data}'")
                
        return " ".join(parts)

