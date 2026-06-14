-- DRINKOO Seed Data

-- Products (10 DRINKOO beverages)
INSERT INTO products (name, category, description, price, is_bulk_available, is_low_sugar, calories, stock_quantity) VALUES
('Citrus Burst', 'Energy Drink', 'A zesty citrus-flavored energy drink with natural caffeine and vitamin C.', 2.99, 1, 0, 150, 500),
('Berry Splash Zero', 'Sparkling Water', 'Sparkling water infused with mixed berry flavor — zero sugar, zero calories.', 1.79, 1, 1, 0, 800),
('Mango Fusion', 'Juice', 'Cold-pressed mango juice with a hint of ginger. Rich in vitamin A.', 3.49, 0, 0, 130, 300),
('Green Detox', 'Juice', 'Cucumber, spinach, and green apple blend. Low sugar and packed with antioxidants.', 3.99, 0, 1, 60, 200),
('Tropical Storm', 'Energy Drink', 'Pineapple and coconut energy drink with electrolytes for post-workout recovery.', 3.29, 1, 0, 180, 450),
('Sparkling Lemon Mint', 'Sparkling Water', 'Lightly sparkling water with lemon and fresh mint. Low sugar.', 1.99, 1, 1, 10, 700),
('Watermelon Wave', 'Juice', 'Fresh watermelon juice — hydrating and naturally sweet.', 2.79, 0, 0, 90, 350),
('Blueberry Boost', 'Energy Drink', 'Antioxidant-rich blueberry energy drink with B vitamins and natural caffeine.', 3.19, 1, 0, 160, 400),
('Coconut Calm', 'Coconut Water', '100% pure coconut water with potassium and electrolytes. No added sugar.', 2.49, 1, 1, 45, 600),
('Peach Passion Zero', 'Sparkling Water', 'Sparkling peach and passion fruit water — zero sugar and zero calories.', 1.89, 1, 1, 0, 750);

-- Ingredients
INSERT INTO ingredients (name, description, is_allergen) VALUES
('Citric Acid', 'Natural preservative and flavor enhancer.', 0),
('Caffeine', 'Natural stimulant derived from green tea extract.', 0),
('Vitamin C', 'Ascorbic acid — antioxidant and immunity booster.', 0),
('Mango Puree', 'Cold-pressed mango extract.', 0),
('Ginger Extract', 'Root ginger concentrate for digestion support.', 0),
('Spinach Extract', 'Green leafy vegetable extract rich in iron.', 0),
('Cucumber Extract', 'Hydrating vegetable extract.', 0),
('Green Apple Juice', 'Cold-pressed Granny Smith apple juice.', 0),
('Pineapple Juice', 'Tropical fruit juice with bromelain.', 0),
('Coconut Water', 'Natural coconut water with electrolytes.', 0),
('Watermelon Juice', 'Fresh watermelon extract — natural sweetener.', 0),
('Blueberry Extract', 'Antioxidant-rich wild blueberry concentrate.', 0),
('Vitamin B Complex', 'B3, B6, B12 blend for energy metabolism.', 0),
('Mint Extract', 'Natural peppermint oil for freshness.', 0),
('Stevia', 'Natural zero-calorie sweetener from stevia leaf.', 0);

-- Product-Ingredient Relationships
INSERT INTO product_ingredients (product_id, ingredient_id, quantity_mg) VALUES
(1, 1, 200), (1, 2, 80), (1, 3, 100),         -- Citrus Burst
(2, 15, 50), (2, 1, 100),                       -- Berry Splash Zero
(3, 4, 500), (3, 5, 30),                        -- Mango Fusion
(4, 6, 200), (4, 7, 150), (4, 8, 300), (4, 15, 30), -- Green Detox
(5, 9, 400), (5, 10, 300), (5, 2, 80),          -- Tropical Storm
(6, 1, 80), (6, 14, 20), (6, 15, 40),           -- Sparkling Lemon Mint
(7, 11, 600),                                    -- Watermelon Wave
(8, 12, 300), (8, 2, 80), (8, 13, 50),          -- Blueberry Boost
(9, 10, 800),                                    -- Coconut Calm
(10, 15, 50), (10, 1, 80);                      -- Peach Passion Zero

-- Promotions (5 active deals)
INSERT INTO promotions (product_id, title, discount_pct, description, active, starts_at, expires_at) VALUES
(1, 'Summer Energy Sale', 20.0, 'Get 20% off Citrus Burst energy drinks this summer!', 1, '2026-06-01', '2026-08-31'),
(NULL, 'Sparkling Beverages Bundle', 15.0, 'Buy any 3 sparkling water products and save 15%.', 1, '2026-06-01', '2026-07-31'),
(5, 'Workout Wednesday', 10.0, 'Every Wednesday — 10% off Tropical Storm for gym members.', 1, '2026-06-01', '2026-12-31'),
(9, 'Coconut Water Bulk Deal', 25.0, 'Order 24+ Coconut Calm units and save 25%.', 1, '2026-05-01', '2026-09-30'),
(4, 'Detox Week', 30.0, 'Start your detox — Green Detox juices 30% off for one week.', 1, '2026-06-09', '2026-06-16');

-- Support Articles (10 customer support docs)
INSERT INTO support_articles (title, content, category) VALUES
('How to place a bulk order', 'To place a bulk order (12+ units), visit our Bulk Orders page or contact support@drinkoo.com. Bulk pricing is automatically applied at checkout for eligible products. Minimum order is 12 units per SKU. Delivery for bulk orders takes 3-5 business days.', 'Orders'),
('What to do if your order arrives damaged', 'If your DRINKOO order arrives damaged, take photos of the damaged packaging and product within 24 hours. Contact us at support@drinkoo.com with your order number and photos. We will ship a replacement within 48 hours or issue a full refund — your choice. Do not return damaged items without contacting support first.', 'Orders'),
('Subscription cancellation policy', 'You may cancel your DRINKOO subscription at any time from your account dashboard. Cancellations take effect at the end of the current billing period. No partial refunds are issued for unused days. Pausing is also available for up to 3 months.', 'Account'),
('Allergen information', 'DRINKOO products are manufactured in facilities that may handle nuts, soy, and dairy. Each product page lists ingredients and common allergens. Products marked with a leaf icon are vegan. If you have severe allergies, please contact our support team before ordering.', 'Health & Safety'),
('Return and refund policy', 'Unopened products may be returned within 14 days of delivery. Opened products are non-returnable unless defective or damaged. To initiate a return, log in to your account and select the order, then click Return Item. Refunds are processed in 5-7 business days to your original payment method.', 'Returns'),
('Low sugar product guide', 'DRINKOO offers several low-sugar options: Berry Splash Zero (0g sugar), Sparkling Lemon Mint (2g sugar), Green Detox (8g sugar), Coconut Calm (6g sugar), and Peach Passion Zero (0g sugar). All zero-sugar products use stevia as a natural sweetener. Look for the green leaf badge on product pages.', 'Products'),
('Ingredients and nutrition FAQ', 'All DRINKOO products list full ingredient information on the label and product page. Caffeine content: Energy drinks contain 80mg per 330ml can (equivalent to one espresso). Our natural caffeine is sourced from green tea extract. We never use artificial colors or high-fructose corn syrup.', 'Health & Safety'),
('Delivery timeframes', 'Standard delivery takes 2-3 business days. Express delivery (next day) is available for orders placed before 2pm. Bulk orders take 3-5 business days. Free standard shipping on orders over $30. International shipping is not currently available.', 'Shipping'),
('How the DRINKOO loyalty program works', 'Earn 1 point per $1 spent. Points never expire. Redeem 100 points for $5 off your next order. Bonus points events run monthly — check the Promotions page. Points are credited 24 hours after delivery confirmation.', 'Loyalty'),
('Contact DRINKOO support', 'Email: support@drinkoo.com (response within 4 hours on weekdays). Live chat: available on the website Mon-Fri 9am-6pm EST. Phone: 1-800-DRINKOO (1-800-374-6566). For urgent order issues, always include your order number in the subject line.', 'Contact');

-- Sample users (passwords hashed — these are for testing only)
-- Password for all test users is: TestPass123!
-- Hashes generated with bcrypt rounds=12
INSERT INTO users (email, hashed_password, full_name) VALUES
('alice@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Alice Johnson'),
('bob@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Bob Smith');

-- Sample orders
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
(1, 1, 6, 17.94, 'delivered'),
(1, 3, 2, 6.98, 'delivered'),
(2, 5, 24, 79.00, 'processing'),
(2, 9, 12, 29.88, 'shipped'),
(1, 2, 3, 5.37, 'pending');
