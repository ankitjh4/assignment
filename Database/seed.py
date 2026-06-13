"""Seed the DRINKOO database with dummy data. Safe to re-run (INSERT OR IGNORE)."""
import sqlite3
import sys
from pathlib import Path

# Allow running from repo root or from Database/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Backend.services.db_service import init_db, get_db  # noqa: E402


PRODUCTS = [
    ("Citrus Burst", "citrus", "A refreshing citrus blend packed with vitamin C. Light and zesty.", 2.49, 1, 3.5, 1),
    ("Tropical Mango Fizz", "sparkling", "Sparkling mango drink with natural fruit juice and light carbonation.", 2.99, 1, 8.0, 1),
    ("Green Detox Water", "flavored_water", "Cucumber, mint, and lemon infused still water. Zero sugar.", 1.99, 1, 0.0, 1),
    ("Berry Blast Smoothie", "smoothie", "A thick blend of strawberry, blueberry, and raspberry. No added sugar.", 3.49, 1, 4.2, 0),
    ("Energy Rush Cola", "energy", "Cola-flavoured energy drink with caffeine and B-vitamins.", 3.29, 1, 11.0, 1),
    ("Watermelon Chill", "sparkling", "Sparkling watermelon drink, light and summery. Low sugar.", 2.79, 1, 2.8, 1),
    ("Classic Lemonade", "citrus", "Traditional lemonade made with real lemon juice.", 1.99, 1, 9.5, 1),
    ("Pineapple Coconut Splash", "tropical", "Tropical blend of pineapple and coconut water.", 3.19, 1, 6.5, 0),
    ("Mint Green Tea Cooler", "tea", "Chilled green tea with fresh mint. Lightly sweetened.", 2.29, 1, 1.5, 1),
    ("Peach Iced Tea", "tea", "Brewed black tea with peach flavour and ice. Low sugar.", 2.49, 1, 2.2, 1),
]

INGREDIENTS = [
    ("Lemon Juice", "Freshly squeezed lemon juice", None),
    ("Mango Pulp", "100% natural mango pulp", None),
    ("Cucumber Extract", "Cold-pressed cucumber extract", None),
    ("Mint Leaves", "Fresh mint leaf extract", None),
    ("Strawberry Puree", "Blended strawberry puree", None),
    ("Blueberry Concentrate", "Concentrated blueberry juice", None),
    ("Raspberry Puree", "Fresh raspberry puree", None),
    ("Caffeine", "Natural caffeine from green coffee beans", None),
    ("B-Vitamins Complex", "B3, B6, B12 vitamin blend", None),
    ("Watermelon Juice", "Natural watermelon juice", None),
    ("Coconut Water", "Natural coconut water", None),
    ("Pineapple Juice", "Pressed pineapple juice", None),
    ("Green Tea Extract", "Brewed green tea extract", None),
    ("Peach Flavour", "Natural peach flavouring", None),
    ("Carbonated Water", "Purified sparkling water", None),
    ("Citric Acid", "Natural citric acid for tartness", "May cause sensitivity in some individuals"),
    ("Cane Sugar", "Unrefined cane sugar", None),
    ("Stevia", "Natural zero-calorie sweetener from stevia leaf", None),
]

# (product_name, ingredient_name, quantity)
PRODUCT_INGREDIENTS = [
    ("Citrus Burst", "Lemon Juice", "40%"),
    ("Citrus Burst", "Citric Acid", "0.3%"),
    ("Citrus Burst", "Stevia", "0.1%"),
    ("Tropical Mango Fizz", "Mango Pulp", "35%"),
    ("Tropical Mango Fizz", "Carbonated Water", "60%"),
    ("Tropical Mango Fizz", "Cane Sugar", "5%"),
    ("Green Detox Water", "Cucumber Extract", "10%"),
    ("Green Detox Water", "Mint Leaves", "5%"),
    ("Green Detox Water", "Lemon Juice", "5%"),
    ("Berry Blast Smoothie", "Strawberry Puree", "33%"),
    ("Berry Blast Smoothie", "Blueberry Concentrate", "33%"),
    ("Berry Blast Smoothie", "Raspberry Puree", "34%"),
    ("Energy Rush Cola", "Caffeine", "0.03%"),
    ("Energy Rush Cola", "B-Vitamins Complex", "0.02%"),
    ("Energy Rush Cola", "Cane Sugar", "11%"),
    ("Watermelon Chill", "Watermelon Juice", "30%"),
    ("Watermelon Chill", "Carbonated Water", "65%"),
    ("Watermelon Chill", "Stevia", "0.1%"),
    ("Classic Lemonade", "Lemon Juice", "25%"),
    ("Classic Lemonade", "Cane Sugar", "9.5%"),
    ("Pineapple Coconut Splash", "Pineapple Juice", "40%"),
    ("Pineapple Coconut Splash", "Coconut Water", "55%"),
    ("Mint Green Tea Cooler", "Green Tea Extract", "60%"),
    ("Mint Green Tea Cooler", "Mint Leaves", "5%"),
    ("Mint Green Tea Cooler", "Stevia", "0.05%"),
    ("Peach Iced Tea", "Peach Flavour", "10%"),
    ("Peach Iced Tea", "Green Tea Extract", "70%"),
    ("Peach Iced Tea", "Stevia", "0.05%"),
]

SUPPORT_ARTICLES = [
    (
        "What to do if your order arrives damaged",
        "damaged_orders",
        """If your DRINKOO order arrives damaged, please follow these steps:
1. Take a photo of the damaged items and packaging immediately.
2. Contact our support team within 48 hours of delivery via email at support@drinkoo.com or through the chat on our website.
3. Include your order number and the photos in your message.
4. We will arrange a free replacement or full refund within 3–5 business days.
We apologise for any inconvenience and take all damage reports seriously.""",
    ),
    (
        "Bulk order policy and discounts",
        "bulk_orders",
        """DRINKOO offers bulk ordering for businesses, events, and wholesale customers.
Products available for bulk orders are marked 'Bulk Available' on the product page.
Minimum bulk order quantity: 24 units per product.
Bulk discount tiers:
- 24–47 units: 10% discount
- 48–95 units: 15% discount
- 96+ units: 20% discount
To place a bulk order, add items to your cart and select 'Bulk Order' at checkout, or email bulk@drinkoo.com.
Bulk orders are dispatched within 2–4 business days.""",
    ),
    (
        "Return and refund policy",
        "returns",
        """DRINKOO accepts returns and refund requests under the following conditions:
- Unopened products can be returned within 14 days of purchase.
- Damaged or incorrect orders can be reported within 48 hours.
- Refunds are processed to the original payment method within 5–7 business days.
- Opened products are not eligible for return unless they are defective.
To initiate a return, contact support@drinkoo.com with your order number and reason.""",
    ),
    (
        "Allergen and ingredient information",
        "allergens",
        """DRINKOO products are manufactured in a facility that may process nuts, dairy, and gluten.
Each product page lists full ingredients and any allergen information.
Products containing citric acid may cause sensitivity in some individuals.
If you have a specific allergy query, contact our team before ordering.
We label all products clearly and update ingredient lists whenever formulations change.""",
    ),
    (
        "Active promotions and how to apply discount codes",
        "promotions",
        """DRINKOO regularly runs promotions and seasonal discounts.
To apply a discount code: add items to your cart, proceed to checkout, and enter the code in the 'Promo Code' field.
Codes are case-insensitive. Only one code can be applied per order.
Check the Promotions section on our website or the DRINKOO app for currently active offers.
Promotions cannot be combined with bulk order discounts unless stated otherwise.""",
    ),
]

PROMOTIONS = [
    (
        "Summer Splash Sale",
        "Get 20% off all sparkling beverages this summer. Use code SPLASH20 at checkout.",
        20.0,
        "2026-06-01",
        "2026-08-31",
        1,
    ),
    (
        "New Customer Welcome Offer",
        "First-time customers enjoy 15% off their first order. Use code WELCOME15.",
        15.0,
        "2026-01-01",
        "2026-12-31",
        1,
    ),
    (
        "Bulk Buy Bonus",
        "Order 48 or more units and get an extra 5% off on top of the standard bulk discount.",
        5.0,
        "2026-06-01",
        "2026-07-31",
        1,
    ),
    (
        "Citrus Lovers Deal",
        "Buy any two citrus drinks and get the third free. Add three to cart to see the discount.",
        33.0,
        "2026-06-10",
        "2026-06-30",
        1,
    ),
]


def seed():
    init_db()
    conn = get_db()

    # Products
    conn.executemany(
        "INSERT OR IGNORE INTO products (name, category, description, price, is_available, sugar_grams, is_bulk_available) VALUES (?,?,?,?,?,?,?)",
        PRODUCTS,
    )

    # Ingredients
    conn.executemany(
        "INSERT OR IGNORE INTO ingredients (name, description, allergen_info) VALUES (?,?,?)",
        INGREDIENTS,
    )
    conn.commit()

    # Product-ingredient relationships
    for p_name, i_name, qty in PRODUCT_INGREDIENTS:
        p = conn.execute("SELECT id FROM products WHERE name = ?", (p_name,)).fetchone()
        i = conn.execute("SELECT id FROM ingredients WHERE name = ?", (i_name,)).fetchone()
        if p and i:
            conn.execute(
                "INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id, quantity) VALUES (?,?,?)",
                (p["id"], i["id"], qty),
            )

    # Support articles
    conn.executemany(
        "INSERT OR IGNORE INTO support_articles (title, category, content) VALUES (?,?,?)",
        [(a[0], a[1], a[2]) for a in SUPPORT_ARTICLES],
    )

    # Promotions
    conn.executemany(
        "INSERT OR IGNORE INTO promotions (title, description, discount_percent, start_date, end_date, is_active) VALUES (?,?,?,?,?,?)",
        PROMOTIONS,
    )

    conn.commit()
    conn.close()
    print("DRINKOO database seeded successfully.")


if __name__ == "__main__":
    seed()
