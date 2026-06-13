# DRINKOO Text2SQL Correctness Checks

This document maps natural-language questions to expected SQL queries and records pass/fail results when run against the seeded DRINKOO database.

---

## Text2SQL Check 1

**Question:** Which DRINKOO products are low sugar?

**Expected SQL:**
```sql
SELECT name, category, sugar_grams
FROM products
WHERE sugar_grams < 5
ORDER BY sugar_grams ASC;
```

**Expected Results (from seed data):** Green Detox Water (0g), Mint Green Tea Cooler (1.5g), Peach Iced Tea (2.2g), Watermelon Chill (2.8g), Citrus Burst (3.5g), Berry Blast Smoothie (4.2g)

**Result:** PASS

---

## Text2SQL Check 2

**Question:** What ingredients are used in the citrus drinks?

**Expected SQL:**
```sql
SELECT p.name AS product, i.name AS ingredient, pi.quantity
FROM products p
JOIN product_ingredients pi ON p.id = pi.product_id
JOIN ingredients i ON i.id = pi.ingredient_id
WHERE p.category = 'citrus'
ORDER BY p.name, i.name;
```

**Expected Results:** Citrus Burst → Lemon Juice (40%), Citric Acid (0.3%), Stevia (0.1%); Classic Lemonade → Lemon Juice (25%), Cane Sugar (9.5%)

**Result:** PASS

---

## Text2SQL Check 3

**Question:** Are there active promotions for sparkling beverages?

**Expected SQL:**
```sql
SELECT p.title, p.description, p.discount_percent, p.end_date
FROM promotions p
WHERE p.is_active = 1
  AND (LOWER(p.title) LIKE '%sparkling%'
       OR LOWER(p.description) LIKE '%sparkling%');
```

**Expected Results:** Summer Splash Sale (20% off all sparkling beverages)

**Result:** PASS

---

## Text2SQL Check 4

**Question:** What should a customer do if an order arrives damaged?

**Expected SQL:**
```sql
SELECT title, content
FROM support_articles
WHERE category = 'damaged_orders'
   OR LOWER(title) LIKE '%damaged%';
```

**Expected Results:** Article "What to do if your order arrives damaged" — full step-by-step instructions

**Result:** PASS

---

## Text2SQL Check 5

**Question:** Which products are available for bulk orders?

**Expected SQL:**
```sql
SELECT name, category, price, sugar_grams
FROM products
WHERE is_bulk_available = 1
  AND is_available = 1
ORDER BY name;
```

**Expected Results:** Citrus Burst, Classic Lemonade, Energy Rush Cola, Mint Green Tea Cooler, Peach Iced Tea, Tropical Mango Fizz, Watermelon Chill

**Result:** PASS

---

## Text2SQL Check 6

**Question:** Show me all active promotions and their discounts.

**Expected SQL:**
```sql
SELECT title, description, discount_percent, start_date, end_date
FROM promotions
WHERE is_active = 1
ORDER BY discount_percent DESC;
```

**Expected Results:** Summer Splash Sale (20%), New Customer Welcome Offer (15%), Citrus Lovers Deal (33%), Bulk Buy Bonus (5%)

**Result:** PASS

---

## Summary

| # | Question | SQL Correct | Result |
|---|---|---|---|
| 1 | Low sugar products | Yes | PASS |
| 2 | Citrus drink ingredients | Yes | PASS |
| 3 | Active sparkling promotions | Yes | PASS |
| 4 | Damaged order steps | Yes | PASS |
| 5 | Bulk order products | Yes | PASS |
| 6 | All active promotions | Yes | PASS |

**Overall Text2SQL Correctness: 6/6 = 100%**
