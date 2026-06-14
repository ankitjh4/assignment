"""
Data loader script for DRINKOO database.
Creates SQLite database, loads schema, and seeds initial data.
"""
import sqlite3
import os
import sys
import bcrypt
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Database path
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_DIR = PROJECT_DIR / "Database"
DB_PATH = DB_DIR / "drinkoo.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def hash_password_bcrypt(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def create_database():
    """Create database from schema."""
    if DB_PATH.exists():
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Read and execute schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    print(f"✓ Database created at {DB_PATH}")
    return conn


def seed_data(conn):
    """Seed initial test data."""
    cursor = conn.cursor()
    
    # Create hashed passwords for default users
    default_password_hash = hash_password_bcrypt("password123")
    
    # Seed users - including a default test user
    cursor.execute("""
        INSERT INTO users (username, email, password_hash) VALUES
        (?, ?, ?),
        (?, ?, ?),
        (?, ?, ?)
    """, (
        'testuser', 'test@drinkoo.com', default_password_hash,
        'demo_user', 'demo@drinkoo.com', default_password_hash,
        'admin', 'admin@drinkoo.com', default_password_hash
    ))
    
    # Seed ingredients
    cursor.execute("""
        INSERT INTO ingredients (name, description, allergen_flag) VALUES
        ('Orange Juice', 'Fresh orange juice', 0),
        ('Carbonated Water', 'Sparkling water', 0),
        ('Strawberry', 'Fresh strawberries', 0),
        ('Lemon', 'Fresh lemon juice', 0),
        ('Sugar', 'Refined sugar', 0),
        ('Artificial Sweetener', 'Aspartame', 1),
        ('Vanilla Extract', 'Natural vanilla', 0),
        ('Coconut Milk', 'Coconut-based milk', 1),
        ('Honey', 'Organic honey', 0),
        ('Ginger', 'Fresh ginger root', 0)
    """)
    
    # Seed products (DRINKOO SKUs)
    cursor.execute("""
        INSERT INTO products (sku, name, description, unit_volume_ml, category, price_cents) VALUES
        ('SKU-001', 'Orange Splash', 'Refreshing orange juice drink', 330, 'Juice', 350),
        ('SKU-002', 'Berry Fizz', 'Carbonated berry drink', 500, 'Sparkling', 450),
        ('SKU-003', 'Tropical Mix', 'Tropical fruit blend', 250, 'Juice', 300),
        ('SKU-004', 'Lemon Zest', 'Zesty lemon drink', 330, 'Sparkling', 400),
        ('SKU-005', 'Honey Vanilla', 'Sweet honey vanilla beverage', 330, 'Special', 500),
        ('SKU-006', 'Coconut Dream', 'Creamy coconut drink', 250, 'Special', 450)
    """)
    
    # Seed product ingredients
    cursor.execute("""
        INSERT INTO product_ingredients (product_id, ingredient_id, quantity_grams) VALUES
        (1, 1, 250),  -- Orange Splash: Orange Juice
        (1, 2, 80),   -- Orange Splash: Carbonated Water
        (2, 3, 150),  -- Berry Fizz: Strawberry
        (2, 2, 350),  -- Berry Fizz: Carbonated Water
        (2, 5, 50),   -- Berry Fizz: Sugar
        (3, 1, 120),  -- Tropical Mix: Orange Juice
        (3, 3, 80),   -- Tropical Mix: Strawberry
        (4, 4, 200),  -- Lemon Zest: Lemon
        (4, 2, 130),  -- Lemon Zest: Carbonated Water
        (5, 9, 40),   -- Honey Vanilla: Honey
        (5, 7, 5),    -- Honey Vanilla: Vanilla Extract
        (6, 8, 200),  -- Coconut Dream: Coconut Milk
        (6, 9, 30)    -- Coconut Dream: Honey
    """)
    
    # Seed support articles
    cursor.execute("""
        INSERT INTO support_articles (title, content, topic) VALUES
        ('Orange Splash Overview', 'Orange Splash is our signature citrus drink, made from fresh orange juice. Perfect for morning refreshment.', 'Products'),
        ('Berry Fizz Details', 'Berry Fizz combines fresh strawberries with carbonated water for a refreshing, bubbly experience.', 'Products'),
        ('Allergen Information', 'Our drinks may contain traces of nuts and dairy. See product labels for specific allergen details.', 'Allergens'),
        ('Ordering FAQ', 'Orders are processed within 24 hours. Delivery takes 2-3 business days.', 'Orders'),
        ('Nutritional Content', 'All DRINKOO beverages contain natural ingredients with no artificial colors or preservatives.', 'Nutrition'),
        ('Storage Instructions', 'Keep all DRINKOO products refrigerated. Use within 7 days of opening.', 'Storage')
    """)
    
    conn.commit()
    print("✓ Seed data loaded successfully")


def load_text2sql_samples():
    """Return sample natural language questions and expected SQL for validation."""
    return [
        {
            "question": "What orange juice products do we have?",
            "expected_sql": "SELECT DISTINCT p.* FROM products p WHERE p.category = 'Juice' AND p.name LIKE '%Orange%'",
            "explanation": "Text2SQL should identify juice products with orange in name"
        },
        {
            "question": "Which products contain strawberry?",
            "expected_sql": "SELECT DISTINCT p.* FROM products p JOIN product_ingredients pi ON p.id = pi.product_id JOIN ingredients i ON pi.ingredient_id = i.id WHERE i.name = 'Strawberry'",
            "explanation": "Needs join across three tables to find products with strawberry ingredient"
        },
        {
            "question": "What are all sparkling drinks?",
            "expected_sql": "SELECT * FROM products WHERE category = 'Sparkling'",
            "explanation": "Simple category filter"
        },
        {
            "question": "How much does Orange Splash cost?",
            "expected_sql": "SELECT price_cents FROM products WHERE name = 'Orange Splash'",
            "explanation": "Direct product lookup"
        },
        {
            "question": "Show me products under 300ml",
            "expected_sql": "SELECT * FROM products WHERE unit_volume_ml < 300 ORDER BY unit_volume_ml",
            "explanation": "Numeric comparison on volume"
        },
        {
            "question": "What ingredients are in Berry Fizz?",
            "expected_sql": "SELECT i.name, pi.quantity_grams FROM ingredients i JOIN product_ingredients pi ON i.id = pi.ingredient_id JOIN products p ON pi.product_id = p.id WHERE p.name = 'Berry Fizz'",
            "explanation": "Multi-table join to get ingredients for specific product"
        },
        {
            "question": "Which products are allergen-free?",
            "expected_sql": "SELECT DISTINCT p.* FROM products p WHERE p.id NOT IN (SELECT pi.product_id FROM product_ingredients pi JOIN ingredients i ON pi.ingredient_id = i.id WHERE i.allergen_flag = 1)",
            "explanation": "Requires subquery to filter out products with allergen ingredients"
        },
        {
            "question": "Tell me about storage instructions",
            "expected_sql": "SELECT content FROM support_articles WHERE topic = 'Storage'",
            "explanation": "Simple support article retrieval"
        },
        {
            "question": "List all products with prices sorted by cost",
            "expected_sql": "SELECT name, price_cents FROM products ORDER BY price_cents ASC",
            "explanation": "Requires sorting by numeric column"
        },
        {
            "question": "Which products have coconut as ingredient?",
            "expected_sql": "SELECT DISTINCT p.* FROM products p JOIN product_ingredients pi ON p.id = pi.product_id JOIN ingredients i ON pi.ingredient_id = i.id WHERE i.name LIKE '%Coconut%'",
            "explanation": "LIKE-based search within ingredient names"
        }
    ]


def reset_database():
    """Reset database by removing and recreating."""
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print(f"✓ Removed existing database at {DB_PATH}")


if __name__ == "__main__":
    print("DRINKOO Database Setup")
    print("-" * 40)
    
    # Reset if exists
    reset_database()
    
    # Create fresh database
    conn = create_database()
    
    # Seed initial data
    seed_data(conn)
    
    conn.close()
    
    # Display Text2SQL samples
    print("\n✓ Text2SQL Sample Questions for Validation:")
    print("-" * 40)
    samples = load_text2sql_samples()
    for i, sample in enumerate(samples, 1):
        print(f"{i}. Q: {sample['question']}")
        print(f"   Category: {sample['explanation']}")
    
    print(f"\n✓ Database initialization complete!")
    print(f"  Database location: {DB_PATH}")
    print(f"  Schema location: {SCHEMA_PATH}")
