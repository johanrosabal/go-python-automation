from core.api.actions.base_api_action import BaseAPIAction
from core.api.common.api_response import APIResponse
from core.utils.config_manager import ConfigManager
import requests
from requests.auth import HTTPBasicAuth
import time


class OAuthToken(BaseAPIAction):
    """
    Action class to handle OAuth2 token retrieval and lifecycle management.
    Supports reading credentials directly from configuration files or constructor parameters.
    """

    def __init__(
        self,
        session=None,
        config: dict = None,
        token_url: str = None,
        client_id: str = None,
        client_secret: str = None,
        scope: str = None,
        grant_type: str = "client_credentials",
        **kwargs,
    ):
        """
        Initializes OAuthToken.
        
        Args:
            session: Optional requests.Session instance.
            config: Optional config dictionary (e.g. from environment YAML).
            token_url: OAuth2 token endpoint URL.
            client_id: OAuth2 client ID.
            client_secret: OAuth2 client secret.
            scope: OAuth2 scope.
            grant_type: OAuth2 grant type (default: 'client_credentials').
        """
        session = session or requests.Session()
        super().__init__(session)

        # 1. Extract values from config hierarchy if provided or fallback to ConfigManager
        resolved_config = self._resolve_config(config)

        # 2. Parameters explicitly passed take precedence over config
        self.token_url = token_url or resolved_config.get("token_url") or resolved_config.get("url")
        self.client_id = client_id or resolved_config.get("client_id")
        self.client_secret = client_secret or resolved_config.get("client_secret")
        self.scope = scope or resolved_config.get("scope")
        self.grant_type = grant_type or resolved_config.get("grant_type", "client_credentials")

        self.access_token = None
        self.token_type = "Bearer"
        self.expires_at = None
        self.raw_response = None

    def _resolve_config(self, config: dict = None) -> dict:
        """
        Resolves OAuth configuration dictionary from passed config or ConfigManager.
        Supports various YAML structures:
          - oauth: { ... }
          - api: { oauth: { ... } }
          - auth: { ... }
          - root level keys
        """
        if config is None:
            try:
                config = (
                    ConfigManager.get("api.oauth")
                    or ConfigManager.get("oauth")
                    or ConfigManager.get("api.auth")
                    or ConfigManager.get("auth")
                    or ConfigManager.get("api")
                    or {}
                )
            except Exception:
                config = {}

        if not isinstance(config, dict):
            return {}

        # Check for nested oauth/auth blocks
        if "oauth" in config and isinstance(config["oauth"], dict):
            return config["oauth"]
        if "auth" in config and isinstance(config["auth"], dict):
            return config["auth"]
        if "api" in config and isinstance(config["api"], dict):
            api_block = config["api"]
            if "oauth" in api_block and isinstance(api_block["oauth"], dict):
                return api_block["oauth"]
            if "auth" in api_block and isinstance(api_block["auth"], dict):
                return api_block["auth"]

        return config

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Retrieves the OAuth2 access token.
        If a valid cached token exists and force_refresh is False, returns the cached token.

        Returns:
            str: Access token string.

        Raises:
            ValueError: If required configuration (token_url, client_id, client_secret) is missing.
            RuntimeError: If the token endpoint returns an error.
        """
        if not force_refresh and self.is_token_valid():
            return self.access_token

        if not self.token_url:
            raise ValueError("OAuth 'token_url' is not configured.")
        if not self.client_id or not self.client_secret:
            raise ValueError("OAuth 'client_id' and 'client_secret' must be configured.")

        payload = {
            "grant_type": self.grant_type,
        }
        if self.scope:
            payload["scope"] = self.scope

        auth = HTTPBasicAuth(self.client_id, self.client_secret)

        self._log_request("POST (OAuth Token)", self.token_url, data=payload)
        
        response = self.session.post(
            self.token_url,
            data=payload,
            auth=auth,
        )
        
        self._log_response(response)
        self.raw_response = APIResponse(response)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.token_type = token_data.get("token_type", "Bearer")
            expires_in = token_data.get("expires_in")
            if expires_in:
                # Store expiration with a 60-second safety buffer
                self.expires_at = time.time() + int(expires_in) - 60
            self.logger.info("✅ OAuth Token successfully retrieved and cached.")
            return self.access_token
        else:
            error_msg = f"OAuth token request failed with status {response.status_code}: {response.text}"
            self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

    def is_token_valid(self) -> bool:
        """Checks if the cached token exists and has not expired."""
        if not self.access_token:
            return False
        if self.expires_at and time.time() >= self.expires_at:
            return False
        return True

    def get_bearer_header(self, force_refresh: bool = False) -> dict:
        """Returns the HTTP Authorization header with the Bearer token."""
        token = self.get_token(force_refresh=force_refresh)
        return {"Authorization": f"Bearer {token}"}

    def get_auth_header(self, force_refresh: bool = False) -> dict:
        """Alias for get_bearer_header."""
        return self.get_bearer_header(force_refresh=force_refresh)

    @classmethod
    def from_config(cls, config: dict, session=None) -> "OAuthToken":
        """Factory method to instantiate OAuthToken directly from a configuration dictionary."""
        return cls(session=session, config=config)
