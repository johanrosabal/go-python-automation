import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from core.utils.logger_config import setup_logger
from core.utils.config_manager import ConfigManager


class DBClient:
    """
    Enterprise Multi-Database Client using SQLAlchemy.
    Supports multiple simultaneous named connections defined under `databases.connections.<alias>`
    in the environment YAML (PostgreSQL, MySQL, SQL Server, Oracle, SQLite) with automatic
    `b64:` / `ENC:` password decoding and connection pooling.
    """
    _instances: Dict[str, "DBClient"] = {}

    def __init__(self, connection_name: str = None):
        """
        Initializes a database client for a specific connection alias from `databases.connections`
        (or `databases.default_connection` when `connection_name` is None).
        Also accepts legacy dot-notation keys like `'database.url'`.

        Args:
            connection_name (str, optional): Connection alias in `databases.connections`
                                             (e.g., 'primary', 'orders_db', 'audit_db').
        """
        resolved_alias = (
            None if connection_name in (None, "database.url") else connection_name
        )
        self.db_config = ConfigManager.get_database(resolved_alias)
        self.connection_name = self.db_config.get("name", resolved_alias or "primary")
        self.logger = setup_logger(f"DBClient[{self.connection_name}]")
        self.connection_url = self.db_config.get("url")

        if not self.connection_url:
            self.logger.warning(
                f"No database URL or engine configured for connection: '{self.connection_name}'"
            )
            self.engine = None
            self._session_factory = None
            return

        try:
            # Ensure parent directory exists for file-based SQLite databases
            if self.connection_url.startswith("sqlite:///") and ":memory:" not in self.connection_url:
                sqlite_path = Path(self.connection_url.replace("sqlite:///", "", 1))
                if sqlite_path.parent and not sqlite_path.parent.exists():
                    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

            engine_kwargs: Dict[str, Any] = {"pool_pre_ping": True}
            if not self.connection_url.startswith("sqlite"):
                engine_kwargs["pool_size"] = int(self.db_config.get("pool_size", 5))
                engine_kwargs["max_overflow"] = int(self.db_config.get("max_overflow", 10))

            self.engine = create_engine(self.connection_url, **engine_kwargs)
            self._session_factory = scoped_session(sessionmaker(bind=self.engine))
            self.logger.info(
                f"Database engine initialized for connection '{self.connection_name}'"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to initialize database engine for '{self.connection_name}': {e}"
            )
            self.engine = None
            self._session_factory = None

    @classmethod
    def for_connection(cls, connection_name: str = None) -> "DBClient":
        """
        Returns a cached `DBClient` instance for the requested `connection_name`
        within the active environment (`ConfigManager.get_env()`).
        """
        env = ConfigManager.get_env() or "qa"
        alias = connection_name or ConfigManager.get_default_database()
        cache_key = f"{env}:{alias}"
        if cache_key not in cls._instances or cls._instances[cache_key].engine is None:
            cls._instances[cache_key] = cls(alias)
        return cls._instances[cache_key]

    def execute_query(self, query: str, params: dict = None) -> Optional[List[Dict[str, Any]]]:
        """
        Executes a parameterized SQL query.
        Returns a list of row dictionaries for `SELECT` queries, or commits and returns None for DML.
        """
        if not self.engine:
            raise RuntimeError(
                f"Database engine for connection '{self.connection_name}' is not initialized."
            )

        self.logger.debug(
            f"[{self.connection_name}] Executing SQL: {query} | Params: {params or {}}"
        )
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            if result.returns_rows:
                return [dict(row._mapping) for row in result]
            connection.commit()
            return None

    def fetch_all(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """
        Executes a `SELECT` query and returns all rows as a list of dictionaries.
        """
        rows = self.execute_query(query, params)
        return rows if rows is not None else []

    def fetch_one(self, query: str, params: dict = None) -> Optional[Dict[str, Any]]:
        """
        Executes a `SELECT` query and returns the first row as a dictionary (or None if empty).
        """
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def fetch_value(self, query: str, params: dict = None, column: str = None) -> Any:
        """
        Executes a `SELECT` query and returns a single scalar value from the first row
        (useful for `SELECT COUNT(*)`, `SELECT status`, etc.).
        """
        row = self.fetch_one(query, params)
        if not row:
            return None
        if column:
            return row.get(column)
        return next(iter(row.values()), None)

    def execute(self, query: str, params: dict = None) -> int:
        """
        Executes an `INSERT`, `UPDATE`, `DELETE`, or DDL statement and returns affected rowcount.
        """
        if not self.engine:
            raise RuntimeError(
                f"Database engine for connection '{self.connection_name}' is not initialized."
            )

        self.logger.debug(
            f"[{self.connection_name}] Executing DML: {query} | Params: {params or {}}"
        )
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            connection.commit()
            return result.rowcount

    def get_session(self):
        """Returns a new SQLAlchemy ORM session for this connection."""
        if not self._session_factory:
            raise RuntimeError(
                f"Database session factory for '{self.connection_name}' is not initialized."
            )
        return self._session_factory()

    def close_all(self):
        """Closes all pooled connections for this engine."""
        if self.engine:
            self.engine.dispose()
            self.logger.info(f"Database connections closed for '{self.connection_name}'.")

    @classmethod
    def close_all_cached(cls):
        """Disposes all cached DBClient engines across all connections."""
        for client in cls._instances.values():
            client.close_all()
        cls._instances.clear()
