"""
Database connection and utilities for DRINKOO.
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Optional, List, Dict, Any
from backend.config import Config

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages SQLite database connections."""
    
    def __init__(self, db_path: str = Config.DATABASE_URL):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Create database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            self._connection = conn
            logger.info(f"Connected to database: {self.db_path}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            self.close()


# Global database instance
db = DatabaseConnection()


def get_db_connection() -> sqlite3.Connection:
    """Get database connection for dependency injection."""
    return db.connect()


def execute_query(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute SELECT query and return results as list of dicts."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}\nSQL: {sql}")
        raise


def execute_update(sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE query. Returns number of affected rows."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.rowcount
    except sqlite3.Error as e:
        logger.error(f"Update execution error: {e}\nSQL: {sql}")
        raise


def execute_insert(sql: str, params: tuple = ()) -> int:
    """Execute INSERT query. Returns the inserted row ID."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert execution error: {e}\nSQL: {sql}")
        raise


def check_db_health() -> Dict[str, Any]:
    """Check database connectivity and readiness."""
    health = {
        "status": "unknown",
        "message": "",
        "tables_count": 0,
        "can_read": False,
        "can_write": False
    }
    
    try:
        # Test connectivity
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            health["tables_count"] = cursor.fetchone()[0]
            health["can_read"] = True
            
            # Test write capability
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                         ("__health_check__", "__health_check__@test.local", "test"))
            cursor.execute("DELETE FROM users WHERE username = '__health_check__'")
            health["can_write"] = True
            
            health["status"] = "healthy"
            health["message"] = f"Database ready ({health['tables_count']} tables)"
            
    except sqlite3.IntegrityError:
        # Username already exists, that's fine - means DB is working
        health["status"] = "healthy"
        health["can_read"] = True
        health["can_write"] = True
        health["message"] = "Database ready"
    except Exception as e:
        health["status"] = "unhealthy"
        health["message"] = f"Database error: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    
    return health
