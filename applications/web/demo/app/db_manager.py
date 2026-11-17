from typing import Optional, Dict, Any, List
from core.utils.db_client import DBClient


class DBManager:
    """
    Application-specific Multi-Database Manager for SauceDemo.
    Provides access to both the default connection (`primary`) and any named
    database connection defined under `databases.connections.<alias>` in the environment YAML.
    """

    def __init__(self, default_connection: str = None):
        self._default_connection = default_connection

    @property
    def client(self) -> DBClient:
        """Returns the cached `DBClient` for the default database connection."""
        return DBClient.for_connection(self._default_connection)

    def connection(self, connection_name: str) -> DBClient:
        """
        Returns a cached `DBClient` for any named connection in `databases.connections`
        (e.g., `self.app.db.connection("orders_db")` or `self.app.db.connection("audit_db")`).
        """
        return DBClient.for_connection(connection_name)

    def get_user_by_username(self, username: str, connection_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Example query to fetch a user record by username from the specified (or default) database.
        """
        query = "SELECT * FROM users WHERE username = :username"
        return DBClient.for_connection(connection_name).fetch_one(query, {"username": username})

    def get_orders_by_user(self, username: str) -> List[Dict[str, Any]]:
        """
        Example query against the secondary `'orders_db'` connection.
        """
        query = "SELECT * FROM orders WHERE username = :username"
        return self.connection("orders_db").fetch_all(query, {"username": username})

    def create_test_data(self):
        """Example of seeding data before a test."""
        query = "INSERT INTO users (username, password) VALUES (:u, :p)"
        self.client.execute(query, {"u": "test_user", "p": "test_pass"})

    def cleanup_test_data(self):
        """Example of cleaning up data after a test."""
        query = "DELETE FROM users WHERE username = :u"
        self.client.execute(query, {"u": "test_user"})
