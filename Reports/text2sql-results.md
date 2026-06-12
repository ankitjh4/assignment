# DRINKOO Text2SQL Evaluation Results

Samples: 14
Correct: 12
Correctness: 85.7%
Threshold: 90%
Status: FAIL

## Per-sample results

- [PASS] `low_sugar` -> SELECT id, name, sugar_g_per_100ml FROM products WHERE sugar_g_per_100ml < 4 ORDER BY sugar_g_per_100ml ASC LIMIT 100
- [PASS] `sparkling_bulk` -> SELECT id, name, sku, category, flavor, price_cents, currency FROM products WHERE is_sparkling = 1 AND supports_bulk = 1 ORDER BY name ASC LIMIT 100
- [PASS] `active_citrus_promos` -> SELECT id, code, title FROM promotions WHERE is_active = 1 AND applies_to_category = 'citrus' ORDER BY id ASC LIMIT 100
- [FAIL] `citrus_zing_ingredients` -> SELECT i.name, pi.percentage FROM products AS p JOIN product_ingredients AS pi ON pi.product_id = p.id JOIN ingredients AS i ON i.id = pi.ingredient_id LIMIT 100
- [PASS] `top3_by_qty` -> SELECT p.id, p.name, SUM(oi.qty) AS total_qty FROM order_items AS oi JOIN products AS p ON p.id = oi.product_id GROUP BY p.id, p.name ORDER BY total_qty DESC LIMIT 3
- [PASS] `refund_timeline_article` -> SELECT id, title, body, updated_at FROM support_articles WHERE title LIKE '%refund timeline%' OR slug LIKE '%refund%timeline%' ORDER BY updated_at DESC LIMIT 1
- [PASS] `zero_sugar` -> SELECT id, name, sugar_g_per_100ml FROM products WHERE sugar_g_per_100ml = 0 ORDER BY name ASC LIMIT 100
- [PASS] `tea_products` -> SELECT id, name, category FROM products WHERE category = 'tea' ORDER BY id ASC LIMIT 100
- [FAIL] `active_promo_count` -> SELECT COUNT(*) FROM promotions WHERE is_active = 1 LIMIT 100
- [PASS] `bulk_eligible_products` -> SELECT id, sku, name FROM products WHERE supports_bulk = 1 AND in_stock = 1 ORDER BY id ASC LIMIT 100
- [PASS] `orders_for_demo_user` -> SELECT o.id, o.status FROM orders AS o JOIN users AS u ON u.id = o.user_id WHERE u.email = 'demo@drinkoo.test' ORDER BY o.id ASC LIMIT 100
- [PASS] `allergen_ingredients` -> SELECT id, name FROM ingredients WHERE allergen_flag = 1 ORDER BY id ASC LIMIT 100
- [PASS] `products_with_ginger` -> SELECT p.id, p.name FROM products AS p JOIN product_ingredients AS pi ON pi.product_id = p.id JOIN ingredients AS i ON i.id = pi.ingredient_id WHERE i.name = 'Ginger Extract' ORDER BY p.name ASC LIMIT 100
- [PASS] `kids_low_price` -> SELECT id, name, price_cents FROM products WHERE category = 'kids' AND price_cents < 200 ORDER BY price_cents ASC LIMIT 100