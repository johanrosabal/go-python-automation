import os
import re
import json
import logging
from typing import Optional, Dict, Any
from core.utils.logger_config import setup_logger

logger = setup_logger("VaultManager")

# Regex pattern to identify vault URIs
# Examples:
#   vault:azure://my-vault-name/secret-key
#   vault:aws://corp/qa/database#password
#   vault:hvac://secret/data/qa#api_key
_VAULT_URI_PATTERN = re.compile(r"^vault:(azure|aws|hashicorp|hvac)://([^#]+)(?:#(.+))?$", re.IGNORECASE)


class BaseVaultProvider:
    """Abstract base provider for enterprise cloud key vaults."""
    def get_secret(self, target: str, sub_key: Optional[str] = None) -> Optional[str]:
        raise NotImplementedError


class AzureKeyVaultProvider(BaseVaultProvider):
    """
    Adapter for Azure Key Vault.
    URI format: vault:azure://<vault_name>/<secret_name>
    """
    def __init__(self):
        self._clients: Dict[str, Any] = {}

    def get_secret(self, target: str, sub_key: Optional[str] = None) -> Optional[str]:
        # target is typically "<vault_name>/<secret_name>"
        parts = target.strip("/").split("/", 1)
        if len(parts) != 2:
            logger.warning(f"[AzureVault] Invalid URI format '{target}'. Expected 'vault-name/secret-name'.")
            return None

        vault_name, secret_name = parts[0], parts[1]

        # 1. Attempt Cloud Fetch via azure-keyvault-secrets (Lazy Import)
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            vault_url = f"https://{vault_name}.vault.azure.net"
            if vault_url not in self._clients:
                credential = DefaultAzureCredential()
                self._clients[vault_url] = SecretClient(vault_url=vault_url, credential=credential)

            client = self._clients[vault_url]
            retrieved = client.get_secret(secret_name)
            logger.info(f"[AzureVault] Successfully retrieved secret '{secret_name}' from vault '{vault_name}'.")
            return retrieved.value
        except ImportError:
            logger.debug(
                f"[AzureVault] 'azure-keyvault-secrets' or 'azure-identity' not installed. "
                f"Falling back to local environment variable '{secret_name}'."
            )
        except Exception as e:
            logger.warning(f"[AzureVault] Failed to retrieve '{secret_name}' from Azure: {e}. Falling back to env.")

        # 2. Local Fallback to Environment Variable
        env_fallback = os.getenv(secret_name.upper().replace("-", "_")) or os.getenv(secret_name)
        if env_fallback:
            return env_fallback
        return None


class AWSSecretsManagerProvider(BaseVaultProvider):
    """
    Adapter for AWS Secrets Manager.
    URI format: vault:aws://<secret_name_or_arn>[#<json_key>]
    """
    def __init__(self):
        self._client = None

    def get_secret(self, target: str, sub_key: Optional[str] = None) -> Optional[str]:
        secret_id = target.strip("/")

        # 1. Attempt Cloud Fetch via boto3 (Lazy Import)
        try:
            import boto3

            if not self._client:
                region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
                self._client = boto3.client("secretsmanager", region_name=region)

            response = self._client.get_secret_value(SecretId=secret_id)
            secret_str = response.get("SecretString")

            if secret_str:
                if sub_key:
                    # Secret is a JSON object with key-value pairs
                    data = json.loads(secret_str)
                    return data.get(sub_key)
                return secret_str
        except ImportError:
            logger.debug(
                f"[AWSSecretsManager] 'boto3' not installed. "
                f"Falling back to local environment variable for secret '{secret_id}'."
            )
        except Exception as e:
            logger.warning(f"[AWSSecretsManager] Failed to retrieve '{secret_id}' from AWS: {e}. Falling back to env.")

        # 2. Local Fallback to Environment Variable
        lookup_key = sub_key if sub_key else secret_id.split("/")[-1]
        env_fallback = os.getenv(lookup_key.upper().replace("-", "_")) or os.getenv(lookup_key)
        return env_fallback


class HashiCorpVaultProvider(BaseVaultProvider):
    """
    Adapter for HashiCorp Vault.
    URI format: vault:hvac://<path_to_secret>[#<key_name>]
    """
    def __init__(self):
        self._client = None

    def get_secret(self, target: str, sub_key: Optional[str] = None) -> Optional[str]:
        secret_path = target.strip("/")

        # 1. Attempt Vault Fetch via hvac (Lazy Import)
        try:
            import hvac

            vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
            vault_token = os.getenv("VAULT_TOKEN")

            if not self._client:
                self._client = hvac.Client(url=vault_addr, token=vault_token)

            if self._client.is_authenticated():
                # Read secret (KV engine v2 or v1)
                read_data = self._client.secrets.kv.read_secret_version(path=secret_path)
                data = read_data.get("data", {}).get("data", {})
                if sub_key:
                    return data.get(sub_key)
                return json.dumps(data)
        except ImportError:
            logger.debug(
                f"[HashiCorpVault] 'hvac' not installed. "
                f"Falling back to local environment variable for secret '{secret_path}'."
            )
        except Exception as e:
            logger.warning(f"[HashiCorpVault] Failed to retrieve '{secret_path}' from Vault: {e}. Falling back to env.")

        # 2. Local Fallback to Environment Variable
        lookup_key = sub_key if sub_key else secret_path.split("/")[-1]
        env_fallback = os.getenv(lookup_key.upper().replace("-", "_")) or os.getenv(lookup_key)
        return env_fallback


class VaultManager:
    """
    Central Coordinator for Enterprise Cloud Vault Resolution.
    Decoupled and zero-risk: if providers/libraries are not installed or offline,
    it falls back cleanly to local environment variables without raising unhandled exceptions.
    """
    _providers = {
        "azure": AzureKeyVaultProvider(),
        "aws": AWSSecretsManagerProvider(),
        "hashicorp": HashiCorpVaultProvider(),
        "hvac": HashiCorpVaultProvider(),
    }

    @classmethod
    def is_vault_uri(cls, value: str) -> bool:
        """Checks if a string conforms to the `vault:<provider>://...` scheme."""
        if not isinstance(value, str):
            return False
        return bool(_VAULT_URI_PATTERN.match(value.strip()))

    @classmethod
    def resolve_vault_secret(cls, value: str) -> str:
        """
        Parses and resolves a `vault:<provider>://<target>[#<sub_key>]` URI.
        Returns the resolved plaintext secret, or the original value if not a vault URI.
        """
        if not isinstance(value, str):
            return value

        match = _VAULT_URI_PATTERN.match(value.strip())
        if not match:
            return value

        provider_name = match.group(1).lower()
        target = match.group(2)
        sub_key = match.group(3)

        provider = cls._providers.get(provider_name)
        if not provider:
            logger.warning(f"[VaultManager] Unsupported vault provider '{provider_name}'. Returning raw URI.")
            return value

        resolved = provider.get_secret(target, sub_key)
        if resolved is not None:
            return resolved

        logger.warning(f"[VaultManager] Could not resolve secret from '{value}'. Returning raw URI.")
        return value

