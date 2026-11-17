import base64
import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Optional

_ENV_FILE_LOADED = False


def _load_dotenv_if_present() -> None:
    """
    Loads key=value pairs from the workspace root `.env` file into `os.environ`
    (if `.env` exists and variables are not already set in the environment).
    """
    global _ENV_FILE_LOADED
    if _ENV_FILE_LOADED:
        return
    _ENV_FILE_LOADED = True

    env_path = Path(".env")
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def encode_base64(text: str) -> str:
    """Encodes a plain string to Base64."""
    if text is None:
        return ""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def decode_base64(encoded_text: str) -> str:
    """Decodes a Base64 string back to plain text."""
    if encoded_text is None:
        return ""
    return base64.b64decode(encoded_text.encode("utf-8")).decode("utf-8")


def generate_secret_key() -> str:
    """Generates a random 256-bit URL-safe secret key for `FRAMEWORK_SECRET_KEY`."""
    return secrets.token_urlsafe(32)


def _derive_keystream(secret_key: str, nonce: bytes, length: int) -> bytes:
    """Derives a deterministic cryptographic keystream using SHA-256 CTR-mode HMAC."""
    output = bytearray()
    counter = 0
    key_bytes = secret_key.encode("utf-8")
    while len(output) < length:
        block = hmac.new(
            key_bytes,
            nonce + counter.to_bytes(4, "big"),
            hashlib.sha256,
        ).digest()
        output.extend(block)
        counter += 1
    return bytes(output[:length])


def encrypt_secret(plain_text: str, secret_key: Optional[str] = None) -> str:
    """
    Encrypts `plain_text` using HMAC-SHA256 authenticated stream cipher with a random 16-byte nonce
    and 16-byte authentication tag, returning a `"ENC:..."` prefixed token ready for YAML/JSON files.
    """
    _load_dotenv_if_present()
    key = secret_key or os.getenv("FRAMEWORK_SECRET_KEY")
    if not key:
        raise ValueError(
            "Missing 'FRAMEWORK_SECRET_KEY'. Set it in your '.env' file or OS environment variables."
        )
    plaintext_bytes = plain_text.encode("utf-8")
    nonce = secrets.token_bytes(16)
    keystream = _derive_keystream(key, nonce, len(plaintext_bytes))
    ciphertext = bytes(a ^ b for a, b in zip(plaintext_bytes, keystream))
    mac = hmac.new(key.encode("utf-8"), nonce + ciphertext, hashlib.sha256).digest()[:16]
    token = base64.urlsafe_b64encode(nonce + mac + ciphertext).decode("utf-8")
    return f"ENC:{token}"


def decrypt_secret(encrypted_token: str, secret_key: Optional[str] = None) -> str:
    """
    Decrypts an `"ENC:..."` token using `FRAMEWORK_SECRET_KEY` and verifies its integrity tag.
    """
    _load_dotenv_if_present()
    key = secret_key or os.getenv("FRAMEWORK_SECRET_KEY")
    if not key:
        raise ValueError(
            "Cannot decrypt 'ENC:...' value because 'FRAMEWORK_SECRET_KEY' is not set in '.env' or environment."
        )
    raw_b64 = encrypted_token[4:].strip() if encrypted_token.upper().startswith("ENC:") else encrypted_token.strip()
    payload = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
    nonce, mac, ciphertext = payload[:16], payload[16:32], payload[32:]
    expected_mac = hmac.new(key.encode("utf-8"), nonce + ciphertext, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("Invalid 'FRAMEWORK_SECRET_KEY' or corrupted 'ENC:...' secret.")
    keystream = _derive_keystream(key, nonce, len(ciphertext))
    plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, keystream))
    return plaintext_bytes.decode("utf-8")


def resolve_secret_value(value: str) -> str:
    """
    Resolves a string according to its prefix (case-insensitive):
      1. `b64:<payload>`   -> Decodes from Base64.
      2. `enc:<payload>`   -> Decrypts using `FRAMEWORK_SECRET_KEY` (from `.env` or OS env).
      3. `vault:<uri>`     -> Resolves from Cloud Vault (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)
                              with graceful fallback to environment variables.
      4. No prefix         -> Returns the plain text string untouched.
    """
    if not isinstance(value, str):
        return value
    upper = value.upper()
    if upper.startswith("B64:"):
        return decode_base64(value[4:].strip())
    if upper.startswith("ENC:"):
        return decrypt_secret(value)
    if upper.startswith("VAULT:"):
        try:
            from core.utils.vault_manager import VaultManager
            return VaultManager.resolve_vault_secret(value)
        except Exception:
            return value
    return value


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python -m core.utils.base64_utils b64 <plain_password>")
        print("  python -m core.utils.base64_utils enc <plain_password> [secret_key]")
        print("  python -m core.utils.base64_utils genkey")
        sys.exit(0)

    mode = sys.argv[1].lower()
    if mode == "genkey":
        print(f"FRAMEWORK_SECRET_KEY={generate_secret_key()}")
    elif mode == "b64":
        print(f"b64:{encode_base64(sys.argv[2])}")
    elif mode == "enc":
        custom_key = sys.argv[3] if len(sys.argv) > 3 else None
        print(encrypt_secret(sys.argv[2], custom_key))
