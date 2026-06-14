"""
Database tests.
Verifies schema, constraints, and data integrity.
"""
import pytest
import sqlite3
from pathlib import Path
from backend.database import execute_query, execute_insert, check_db_health

DATABASE_PATH = "Database/drinkoo.db"


@pytest.fixture
def db_connection():
    """Provide database connection for tests."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


class TestSchemaIntegrity:
    """Test database schema integrity."""
    
    def test_all_tables_exist(self, db_connection):
        """Test that all required tables exist."""
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'users', 'products', 'ingredients', 'product_ingredients',
            'orders', 'support_articles', 'promotions', 'chat_sessions'
        ]
        
        for table in required_tables:
            assert table in tables, f"Missing table: {table}"
    
    def test_users_table_schema(self, db_connection):
        """Test users table schema."""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'id' in columns
        assert 'username' in columns
        assert 'email' in columns
        assert 'password_hash' in columns
    
    def test_products_table_schema(self, db_connection):
        """Test products table schema with constraints."""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'id' in columns
        assert 'sku' in columns
        assert 'name' in columns
        assert 'unit_volume_ml' in columns
    
    def test_foreign_key_constraints(self, db_connection):
        """Test foreign key constraints."""
        cursor = db_connection.cursor()
        
        # Check that product_ingredients references products and ingredients
        cursor.execute("PRAGMA foreign_key_list(product_ingredients)")
        fks = cursor.fetchall()
        
        assert len(fks) > 0, "No foreign keys found"


class TestDataConstraints:
    """Test data constraints and validations."""
    
    def test_volume_constraint(self, db_connection):
        """Test unit_volume_ml CHECK constraint."""
        cursor = db_connection.cursor()
        
        # Valid volumes
        valid_volumes = [250, 330, 500, 1000, 1500, 2000]
        for volume in valid_volumes:
            cursor.execute("""
                INSERT INTO products (sku, name, unit_volume_ml)
                VALUES (?, ?, ?)
            """, (f"TEST-VOL-{volume}", f"Test {volume}ml", volume))
        
        db_connection.commit()
        
        # Invalid volume should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO products (sku, name, unit_volume_ml)
                VALUES (?, ?, ?)
            """, ("TEST-INVALID", "Test Invalid", 999))
            db_connection.commit()
    
    def test_unique_constraints(self, db_connection):
        """Test unique constraints."""
        cursor = db_connection.cursor()
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, ("testuser", "test@example.com", "hash"))
        db_connection.commit()
        
        # Try to insert duplicate username
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, ("testuser", "other@example.com", "hash"))
            db_connection.commit()


class TestDataIntegrity:
    """Test data integrity and relationships."""
    
    def test_product_ingredient_relationship(self, db_connection):
        """Test product-ingredient relationships."""
        cursor = db_connection.cursor()
        
        # Check that we can retrieve product with ingredients
        cursor.execute("""
            SELECT p.name, i.name, pi.quantity_grams
            FROM products p
            JOIN product_ingredients pi ON p.id = pi.product_id
            JOIN ingredients i ON pi.ingredient_id = i.id
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        assert result is not None
        assert len(result) == 3  # product name, ingredient name, quantity
    
    def test_cascade_delete(self, db_connection):
        """Test cascade delete on foreign keys."""
        cursor = db_connection.cursor()
        
        # Create test user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, ("cascadetest", "cascade@test.com", "hash"))
        user_id = cursor.lastrowid
        db_connection.commit()
        
        # Create test product
        cursor.execute("""
            INSERT INTO products (sku, name, unit_volume_ml)
            VALUES (?, ?, ?)
        """, ("CASCADE-TEST", "Cascade Test", 250))
        product_id = cursor.lastrowid
        db_connection.commit()
        
        # Create order
        cursor.execute("""
            INSERT INTO orders (user_id, product_id, quantity, total_price_cents)
            VALUES (?, ?, ?, ?)
        """, (user_id, product_id, 1, 100))
        order_id = cursor.lastrowid
        db_connection.commit()
        
        # Delete user - order should cascade delete
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db_connection.commit()
        
        # Check that order is deleted
        cursor.execute("SELECT COUNT(*) FROM orders WHERE id = ?", (order_id,))
        count = cursor.fetchone()[0]
        assert count == 0


class TestDatabaseHealth:
    """Test database health check."""
    
    def test_health_check(self):
        """Test database health check function."""
        health = check_db_health()
        
        assert 'status' in health
        assert 'message' in health
        assert 'tables_count' in health
        assert 'can_read' in health
        assert 'can_write' in health
        
        # Database should be healthy if properly initialized
        assert health['status'] in ['healthy', 'unhealthy']


class TestSeedData:
    """Test seed data integrity."""
    
    def test_seed_data_exists(self):
        """Test that seed data was loaded."""
        users = execute_query("SELECT COUNT(*) as count FROM users")
        products = execute_query("SELECT COUNT(*) as count FROM products")
        ingredients = execute_query("SELECT COUNT(*) as count FROM ingredients")
        
        assert users[0]['count'] >= 2
        assert products[0]['count'] >= 6
        assert ingredients[0]['count'] >= 10
    
    def test_sku_uniqueness(self):
        """Test that all SKUs are unique."""
        results = execute_query("""
            SELECT sku, COUNT(*) as count FROM products
            GROUP BY sku HAVING count > 1
        """)
        
        assert len(results) == 0, "Duplicate SKUs found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
