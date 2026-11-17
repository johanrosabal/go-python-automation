import yaml
import os
import re
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from core.utils.base64_utils import resolve_secret_value, _load_dotenv_if_present

_config_local = threading.local()
_ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")


class ConfigManager:
    """
    Utility class to load and manage environment-specific configurations from YAML files.
    Supports:
      - Nested dot-notation keys (`web.base_url`, `users.roles.standard.username`)
      - Environment variable interpolation (`${VAR:default}`)
      - 3-Tier Flexible Secret Resolution:
          1. Plain text (`secret_sauce`) -> returned as-is
          2. Base64 obfuscation (`b64:c2VjcmV0X3NhdWNl`) -> decoded automatically
          3. Authenticated Encryption (`ENC:...`) -> decrypted via `FRAMEWORK_SECRET_KEY`
      - Role-Based User Credentials (`users.default_role` & `users.roles.<role>`)
    Thread-safe via thread-local storage with process-level fallback.
    """
    _config = None
    _env = None

    @classmethod
    def _resolve_value(cls, value: Any) -> Any:
        """
        Recursively resolves `${ENV_VAR:default}` placeholders and `b64:` / `ENC:` prefixes
        in strings, dicts, and lists. If no prefix is present, returns plain text untouched.
        """
        if isinstance(value, str):
            _load_dotenv_if_present()
            def _replacer(match):
                env_name = match.group(1)
                default_val = match.group(2) if match.group(2) is not None else ""
                return os.getenv(env_name, default_val)
            interpolated = _ENV_VAR_PATTERN.sub(_replacer, value)
            return resolve_secret_value(interpolated)
        if isinstance(value, dict):
            return {k: cls._resolve_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._resolve_value(item) for item in value]
        return value

    @classmethod
    def load_config(cls, app_path: str, env: str = None):
        """
        Loads the YAML configuration for the specified environment.

        Args:
            app_path (str): The absolute or relative path to the application directory
                            (e.g., 'applications/web/demo').
            env (str, optional): The environment name (qa, dev, uat, prod).
                                 If None, it tries to read from the 'ENV' environment variable.
                                 Defaults to 'qa' if neither is provided.
        """
        resolved_env = env.lower() if env else os.getenv('ENV', 'qa').lower()
        _config_local.env = resolved_env
        cls._env = resolved_env

        config_path = Path(app_path) / "config" / "environments" / f"{resolved_env}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found for environment '{resolved_env}' at: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as file:
            loaded = yaml.safe_load(file)
            _config_local.config = loaded
            cls._config = loaded

        return loaded

    @classmethod
    def get(cls, key: str, default=None):
        """
        Retrieves a configuration value by key. Supports nested keys with dot notation
        (e.g., 'web.base_url' or 'users.roles.standard.username') and resolves `${VAR:default}`.
        """
        active_config = getattr(_config_local, "config", cls._config)
        if active_config is None:
            raise ValueError("Configuration not loaded. Call ConfigManager.load_config() first.")

        keys = key.split('.')
        value = active_config
        try:
            for k in keys:
                value = value[k]
            return cls._resolve_value(value)
        except (KeyError, TypeError):
            return default

    @classmethod
    def get_default_role(cls) -> str:
        """
        Returns the configured default user role from `users.default_role` (or 'standard' fallback).
        """
        return cls.get("users.default_role", "standard")

    @classmethod
    def get_user(cls, role: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves the user credentials dictionary for a given role from `users.roles.<role>`.
        If `role` is omitted, uses `users.default_role`.
        Maintains backwards compatibility with legacy `user:` root blocks if `users:` is absent.

        Args:
            role (str, optional): Role key defined under `users.roles` (e.g., 'standard', 'locked', 'admin').

        Returns:
            Dict[str, Any]: Dictionary containing at least `username`, `password`, and `role`.

        Raises:
            KeyError: If the requested role does not exist in `users.roles`.
        """
        target_role = role or cls.get_default_role()
        roles_map = cls.get("users.roles")

        if isinstance(roles_map, dict):
            if target_role in roles_map and isinstance(roles_map[target_role], dict):
                user_info = dict(roles_map[target_role])
                user_info.setdefault("role", target_role)
                return user_info
            # Fallback if a top-level key under `users.<role>` was used directly
            direct_role = cls.get(f"users.{target_role}")
            if isinstance(direct_role, dict) and "username" in direct_role:
                user_info = dict(direct_role)
                user_info.setdefault("role", target_role)
                return user_info
            available = ", ".join(roles_map.keys())
            raise KeyError(
                f"Role '{target_role}' not found in 'users.roles' for environment '{cls.get_env()}'. "
                f"Available roles: [{available}]"
            )

        # Legacy fallback (`user.username` / `user.password` or `<role>_user`)
        if role:
            legacy_role = cls.get(f"{role}_user") or cls.get(role)
            if isinstance(legacy_role, dict) and "username" in legacy_role:
                user_info = dict(legacy_role)
                user_info.setdefault("role", role)
                return user_info

        legacy_user = cls.get("user")
        if isinstance(legacy_user, dict):
            user_info = dict(legacy_user)
            user_info.setdefault("role", target_role)
            return user_info

        return {"role": target_role, "username": None, "password": None}

    @classmethod
    def get_roles(cls) -> Dict[str, Dict[str, Any]]:
        """
        Returns all available user roles configured under `users.roles`.
        """
        roles = cls.get("users.roles", {})
        return roles if isinstance(roles, dict) else {}

    @classmethod
    def get_default_database(cls) -> str:
        """
        Returns the configured default database connection alias from `databases.default_connection`
        (defaults to 'primary').
        """
        return cls.get("databases.default_connection", "primary")

    @classmethod
    def get_database(cls, connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves the database configuration dictionary for a given connection alias from
        `databases.connections.<connection_name>` (or `databases.default_connection` when omitted).
        Automatically resolves `b64:` / `ENC:` / `${ENV_VAR}` in passwords and builds a valid
        SQLAlchemy `url` if structured fields (`engine`, `host`, `port`, `database`, `username`, `password`)
        are provided instead of a raw `url`.

        Maintains backwards compatibility with legacy `database.url` root blocks.
        """
        target_conn = connection_name or cls.get_default_database()
        connections_map = cls.get("databases.connections")

        db_info: Dict[str, Any] = {}
        if isinstance(connections_map, dict):
            if target_conn in connections_map and isinstance(connections_map[target_conn], dict):
                db_info = dict(connections_map[target_conn])
            else:
                direct_conn = cls.get(f"databases.{target_conn}")
                if isinstance(direct_conn, dict):
                    db_info = dict(direct_conn)
                else:
                    available = ", ".join(connections_map.keys())
                    raise KeyError(
                        f"Database connection '{target_conn}' not found in 'databases.connections' "
                        f"for environment '{cls.get_env()}'. Available connections: [{available}]"
                    )
        else:
            # Legacy fallback (`database.url` or custom dot-key like `database.url`)
            if connection_name and "." in connection_name:
                raw_url = cls.get(connection_name)
                if isinstance(raw_url, str):
                    db_info = {"url": raw_url}
                elif isinstance(raw_url, dict):
                    db_info = dict(raw_url)
            if not db_info:
                legacy_db = cls.get("database")
                if isinstance(legacy_db, dict):
                    db_info = dict(legacy_db)

        db_info.setdefault("name", target_conn)

        # Build SQLAlchemy URL from structured fields if `url` is not explicitly defined
        if not db_info.get("url") and db_info.get("engine"):
            engine_driver = str(db_info["engine"]).strip()
            db_name = str(db_info.get("database") or db_info.get("db_name") or "").strip()

            if engine_driver.startswith("sqlite"):
                if db_name in (":memory:", ""):
                    db_info["url"] = "sqlite:///:memory:"
                else:
                    db_info["url"] = f"sqlite:///{db_name.lstrip('/')}"
            else:
                from sqlalchemy.engine import URL
                query_params = db_info.get("query") or {}
                if db_info.get("driver") and "driver" not in query_params:
                    query_params = dict(query_params)
                    query_params["driver"] = db_info["driver"]

                sa_url = URL.create(
                    drivername=engine_driver,
                    username=db_info.get("username") or db_info.get("user"),
                    password=db_info.get("password"),
                    host=db_info.get("host", "localhost"),
                    port=int(db_info["port"]) if db_info.get("port") else None,
                    database=db_name or None,
                    query=query_params,
                )
                db_info["url"] = sa_url.render_as_string(hide_password=False)

        return db_info

    @classmethod
    def get_databases(cls) -> Dict[str, Dict[str, Any]]:
        """
        Returns all configured database connections under `databases.connections`.
        """
        conns = cls.get("databases.connections", {})
        return conns if isinstance(conns, dict) else {}

    @classmethod
    def get_env(cls):
        """Returns the current active environment name."""
        return getattr(_config_local, "env", cls._env)
