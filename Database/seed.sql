INSERT OR IGNORE INTO products (id, name, category, sugar_grams, calories, bulk_available)
VALUES
    (1, 'Spark Citrus Zero', 'sparkling', 0, 5, 1),
    (2, 'Tropical Lift', 'energy', 12, 110, 0),
    (3, 'Berry Calm Tea', 'tea', 6, 40, 1),
    (4, 'Lime Soda Lite', 'sparkling', 3, 20, 1);

INSERT OR IGNORE INTO ingredients (id, ingredient_name, allergen_flag)
VALUES
    (1, 'Carbonated Water', 0),
    (2, 'Natural Citrus Flavor', 0),
    (3, 'Green Tea Extract', 0),
    (4, 'Berry Concentrate', 0),
    (5, 'Caffeine', 0);

INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id, amount_label)
VALUES
    (1, 1, 'major'),
    (1, 2, 'minor'),
    (2, 1, 'major'),
    (2, 5, 'minor'),
    (3, 3, 'major'),
    (3, 4, 'minor'),
    (4, 1, 'major'),
    (4, 2, 'minor');

INSERT OR IGNORE INTO support_articles (id, title, article_body, category)
VALUES
    (1, 'Damaged order policy', 'If an order arrives damaged, report within 48 hours with photo proof.', 'orders'),
    (2, 'Bulk order support', 'Bulk ordering is available for selected sparkling and tea products.', 'sales');

INSERT OR IGNORE INTO promotions (id, title, details, active)
VALUES
    (1, 'Sparkling Summer', '10% off sparkling drinks for orders above 20 units.', 1),
    (2, 'Tea Bundle', 'Buy 2 Berry Calm Tea packs and get one free.', 1);
