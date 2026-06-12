-- DRINKOO seed data. Idempotent: uses INSERT OR IGNORE on UNIQUE keys.

INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES
  (1, 'demo@drinkoo.test',  '$2b$12$placeholder.replace.during.signup..............', 'Demo Customer', 'customer'),
  (2, 'admin@drinkoo.test', '$2b$12$placeholder.replace.during.signup..............', 'Drinkoo Admin', 'admin');

INSERT OR IGNORE INTO products (id, sku, name, category, flavor, is_sparkling, sugar_g_per_100ml, calories_per_100ml, price_cents, in_stock, supports_bulk, description) VALUES
  (1,  'DRK-CTZ-330', 'Citrus Zing',         'citrus',    'lemon-lime',      1, 3.5,  18, 199, 1, 1, 'Sparkling citrus drink with lemon and lime. Low sugar, refreshing.'),
  (2,  'DRK-ORG-330', 'Orange Sunrise',      'citrus',    'orange',          1, 4.2,  22, 199, 1, 1, 'Bright sparkling orange beverage made with real orange essence.'),
  (3,  'DRK-GRP-330', 'Grapefruit Glow',     'citrus',    'grapefruit',      1, 3.8,  20, 219, 1, 0, 'Tangy sparkling grapefruit beverage with a clean finish.'),
  (4,  'DRK-BRY-330', 'Berry Bliss',         'berry',     'mixed-berry',     1, 5.0,  26, 229, 1, 1, 'Sparkling mixed-berry blend with hints of raspberry and blueberry.'),
  (5,  'DRK-MNT-330', 'Mint Cooler',         'herbal',    'mint',            1, 2.5,  14, 219, 1, 0, 'Sparkling mint cooler. Crisp and ultra-low sugar.'),
  (6,  'DRK-GNG-330', 'Ginger Kick',         'herbal',    'ginger',          1, 4.8,  24, 229, 1, 1, 'Sharp ginger sparkling drink with a warm finish.'),
  (7,  'DRK-COL-330', 'Cola Classic',        'cola',      'cola',            1, 9.5,  42, 199, 1, 1, 'Classic-style cola. Regular sugar level.'),
  (8,  'DRK-COL-DT0', 'Cola Zero',           'cola',      'cola',            1, 0.0,   1, 199, 1, 1, 'Zero-sugar cola sweetened with stevia.'),
  (9,  'DRK-TEA-500', 'Green Tea Lite',      'tea',       'green-tea',       0, 2.0,  10, 189, 1, 1, 'Lightly sweetened cold-brewed green tea.'),
  (10, 'DRK-TEA-PCH', 'Peach Black Tea',     'tea',       'peach',           0, 5.5,  28, 219, 1, 0, 'Cold-brewed black tea with peach essence.'),
  (11, 'DRK-WTR-750', 'Hydra Still',         'water',     'plain',           0, 0.0,   0, 149, 1, 1, 'Still mineral water from a protected source.'),
  (12, 'DRK-WTR-SPK', 'Hydra Sparkle',       'water',     'plain',           1, 0.0,   0, 159, 1, 1, 'Sparkling mineral water.'),
  (13, 'DRK-KID-200', 'Kiddo Apple',         'kids',      'apple',           0, 4.0,  20, 129, 1, 1, 'Apple drink for kids. No artificial colors.'),
  (14, 'DRK-KID-MNG', 'Kiddo Mango',         'kids',      'mango',           0, 4.5,  22, 129, 1, 1, 'Mango drink for kids. No artificial colors.'),
  (15, 'DRK-SPT-500', 'Sport Boost Citrus',  'sports',    'citrus',          0, 6.0,  30, 249, 1, 1, 'Electrolyte sports drink, citrus flavor.'),
  (16, 'DRK-SPT-BRY', 'Sport Boost Berry',   'sports',    'berry',           0, 6.0,  30, 249, 1, 1, 'Electrolyte sports drink, berry flavor.'),
  (17, 'DRK-COF-250', 'Cold Brew Black',     'coffee',    'coffee',          0, 1.0,   8, 269, 1, 0, 'Cold brew coffee, black. Bold and smooth.'),
  (18, 'DRK-COF-MCH', 'Cold Brew Mocha',     'coffee',    'mocha',           0, 7.5,  60, 289, 1, 0, 'Cold brew coffee with cocoa and a touch of milk.'),
  (19, 'DRK-LMN-500', 'Cloudy Lemonade',     'citrus',    'lemon',           0, 7.0,  36, 199, 1, 1, 'Traditional cloudy lemonade. Bulk-friendly.'),
  (20, 'DRK-CTZ-DT0', 'Citrus Zing Zero',    'citrus',    'lemon-lime',      1, 0.0,   2, 209, 1, 1, 'Zero-sugar version of Citrus Zing.');

INSERT OR IGNORE INTO ingredients (id, name, is_natural, allergen_flag, source_country) VALUES
  (1,  'Carbonated Water', 1, 0, 'USA'),
  (2,  'Cane Sugar',       1, 0, 'Brazil'),
  (3,  'Citric Acid',      1, 0, 'USA'),
  (4,  'Lemon Essence',    1, 0, 'Italy'),
  (5,  'Lime Essence',     1, 0, 'Mexico'),
  (6,  'Orange Essence',   1, 0, 'Spain'),
  (7,  'Grapefruit Essence',1,0, 'USA'),
  (8,  'Mint Extract',     1, 0, 'India'),
  (9,  'Ginger Extract',   1, 0, 'India'),
  (10, 'Berry Concentrate',1, 0, 'Chile'),
  (11, 'Stevia Leaf',      1, 0, 'Paraguay'),
  (12, 'Caffeine',         0, 0, 'USA'),
  (13, 'Black Tea Leaves', 1, 0, 'Sri Lanka'),
  (14, 'Green Tea Leaves', 1, 0, 'Japan'),
  (15, 'Peach Essence',    1, 0, 'Italy'),
  (16, 'Apple Juice Concentrate', 1, 0, 'Poland'),
  (17, 'Mango Puree',      1, 0, 'India'),
  (18, 'Sodium Citrate',   0, 0, 'USA'),
  (19, 'Potassium Citrate',0, 0, 'USA'),
  (20, 'Coffee Beans',     1, 0, 'Colombia'),
  (21, 'Cocoa',            1, 1, 'Ghana'),
  (22, 'Milk Solids',      1, 1, 'USA'),
  (23, 'Caramel Color',    0, 0, 'USA'),
  (24, 'Phosphoric Acid',  0, 0, 'USA'),
  (25, 'Mineral Salts',    1, 0, 'France');

INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id, percentage) VALUES
  (1, 1, 92.0), (1, 3, 0.2), (1, 4, 0.4), (1, 5, 0.4), (1, 2, 3.5),
  (2, 1, 92.0), (2, 3, 0.2), (2, 6, 0.8), (2, 2, 4.2),
  (3, 1, 92.0), (3, 3, 0.2), (3, 7, 0.8), (3, 2, 3.8),
  (4, 1, 90.0), (4, 10, 4.5), (4, 2, 5.0),
  (5, 1, 95.0), (5, 8, 0.5), (5, 11, 0.1),
  (6, 1, 90.0), (6, 9, 1.2), (6, 2, 4.8),
  (7, 1, 86.0), (7, 23, 0.1), (7, 24, 0.05), (7, 2, 9.5), (7, 12, 0.01),
  (8, 1, 95.0), (8, 23, 0.1), (8, 24, 0.05), (8, 11, 0.2), (8, 12, 0.01),
  (9, 14, 0.5), (9, 11, 0.1), (9, 2, 2.0),
  (10, 13, 0.5), (10, 15, 0.4), (10, 2, 5.5),
  (11, 1, 100.0),
  (12, 1, 100.0),
  (13, 16, 12.0),
  (14, 17, 14.0),
  (15, 25, 0.5), (15, 18, 0.1), (15, 19, 0.1), (15, 4, 0.3), (15, 5, 0.3), (15, 2, 6.0),
  (16, 25, 0.5), (16, 18, 0.1), (16, 19, 0.1), (16, 10, 0.5), (16, 2, 6.0),
  (17, 20, 5.0), (17, 12, 0.04),
  (18, 20, 4.5), (18, 21, 1.0), (18, 22, 3.0), (18, 2, 7.5),
  (19, 4, 4.0), (19, 2, 7.0),
  (20, 1, 95.0), (20, 3, 0.2), (20, 4, 0.4), (20, 5, 0.4), (20, 11, 0.2);

INSERT OR IGNORE INTO promotions (id, code, title, description, applies_to_category, discount_pct, starts_at, ends_at, is_active) VALUES
  (1, 'SPARKLE10',   'Sparkling Summer Sale',  'Ten percent off all sparkling drinks for the summer season.', 'citrus',  10, '2025-06-01', '2099-12-31', 1),
  (2, 'BERRY15',     'Berry Bliss Boost',      'Fifteen percent off berry category drinks.',                   'berry',   15, '2025-05-01', '2099-12-31', 1),
  (3, 'BULK20',      'Bulk Order Discount',    'Twenty percent off bulk-eligible products on orders of 24+.',  NULL,      20, '2025-01-01', '2099-12-31', 1),
  (4, 'TEACOZY',     'Tea Comfort Week',       'Ten percent off all tea products.',                            'tea',     10, '2025-09-01', '2099-12-31', 1),
  (5, 'KIDS5',       'Kids Pack Discount',     'Five percent off kids drinks family packs.',                   'kids',     5, '2025-01-01', '2099-12-31', 1),
  (6, 'OLDPROMO',    'Expired Spring Promo',   'Past spring promotion. No longer active.',                     'citrus',  10, '2024-03-01', '2024-05-31', 0),
  (7, 'COFFEEHOLIDAY','Coffee Holiday Promo',  'Expired coffee promotion. Past holiday season.',               'coffee',  15, '2024-11-01', '2024-12-31', 0);

INSERT OR IGNORE INTO support_articles (id, slug, title, body, tags) VALUES
  (1, 'damaged-order',
      'What to do if your DRINKOO order arrives damaged',
      'If your DRINKOO order arrives damaged, take a clear photo of the package and contents within 48 hours of delivery, then submit a claim through your account under My Orders. DRINKOO will replace the damaged units free of charge or issue a refund within 5 business days. Do not consume any product if the seal is broken.',
      'orders,refunds,policy'),
  (2, 'return-policy',
      'DRINKOO return policy',
      'DRINKOO accepts returns within 14 days of delivery for unopened sealed product. Opened beverages cannot be returned for food safety reasons. Refunds are processed to the original payment method within 5 business days of receipt of the returned item.',
      'returns,refunds,policy'),
  (3, 'allergen-info',
      'Allergen information for DRINKOO products',
      'DRINKOO products are produced in facilities that handle cocoa and milk solids. Products in our cold brew mocha line contain cocoa and milk and should be avoided by people with cocoa or dairy allergies. Other DRINKOO products are free of common allergens, but always check the label for the latest information.',
      'allergens,ingredients,safety'),
  (4, 'bulk-pricing',
      'How DRINKOO bulk pricing works',
      'Customers ordering 24 or more units of any bulk-eligible product automatically receive a 20 percent discount via the BULK20 code at checkout. Bulk eligibility is marked on each product page. Bulk shipments are delivered within 5 to 7 business days.',
      'bulk,pricing,orders'),
  (5, 'shipping-zones',
      'DRINKOO shipping zones and delivery times',
      'DRINKOO ships across continental USA in 2 to 4 business days, Canada in 3 to 6 business days, and selected EU countries in 5 to 8 business days. Bulk orders may take 5 to 7 business days regardless of zone.',
      'shipping,delivery,policy'),
  (6, 'refund-timeline',
      'Refund processing timeline',
      'DRINKOO processes refunds within 5 business days of confirming the return or damage claim. The refund will appear on your original payment method within 3 to 10 business days after that depending on your bank or card issuer.',
      'refunds,payments,policy'),
  (7, 'gift-cards',
      'Using DRINKOO gift cards',
      'DRINKOO gift cards can be redeemed at checkout by entering the gift card code. Unused balances stay on the gift card for two years. Gift cards cannot be redeemed for cash and are not refundable.',
      'gift-cards,payments,policy'),
  (8, 'subscription',
      'DRINKOO monthly drink subscription',
      'The DRINKOO monthly subscription delivers a curated set of 12 drinks each month for a flat fee. You can pause or cancel anytime from your account. Subscribers also get early access to limited-edition flavors.',
      'subscription,membership,offers');

INSERT OR IGNORE INTO orders (id, user_id, status, total_cents, currency, placed_at, shipped_at, is_bulk) VALUES
  (1, 1, 'shipped',   1194, 'USD', '2025-05-12 10:01:00', '2025-05-13 09:00:00', 0),
  (2, 1, 'delivered', 4776, 'USD', '2025-05-25 14:20:00', '2025-05-26 11:00:00', 1),
  (3, 1, 'placed',     458, 'USD', '2025-06-01 18:30:00', NULL,                  0),
  (4, 2, 'delivered', 7158, 'USD', '2025-05-10 09:15:00', '2025-05-11 08:00:00', 1),
  (5, 2, 'shipped',    618, 'USD', '2025-06-08 12:00:00', '2025-06-09 09:00:00', 0);

INSERT OR IGNORE INTO order_items (id, order_id, product_id, qty, unit_price_cents) VALUES
  (1, 1, 1,  3, 199), (2, 1, 5,  2, 219),  (3, 1, 11, 1, 149),
  (4, 2, 4, 12, 229),  (5, 2, 2, 12, 199),
  (6, 3, 13, 1, 129), (7, 3, 14, 1, 129),  (8, 3, 11, 1, 149),
  (9, 4, 7, 24, 199),  (10, 4, 8, 12, 199),
  (11, 5, 15, 1, 249), (12, 5, 16, 1, 249), (13, 5, 11, 1, 149);

INSERT OR IGNORE INTO chat_sessions (id, user_id, started_at, last_message_at, message_count) VALUES
  (1, 1, '2025-06-01 10:00:00', '2025-06-01 10:05:00', 4),
  (2, 2, '2025-06-05 17:30:00', '2025-06-05 17:35:00', 3);
