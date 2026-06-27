# Text2SQL Correctness Checks

This file documents natural-language questions and the expected SQL queries for evaluating
Text2SQL correctness. Target: >= 90% correctness on these sample questions.

---

## Question 1

**Natural language:** Which DRINKOO products are low sugar?

**Expected SQL:**
```sql
SELECT id, name, category, calories, price
FROM products
WHERE is_low_sugar = 1
ORDER BY name;
```

**Expected result columns:** id, name, category, calories, price

---

## Question 2

**Natural language:** What ingredients are used in the citrus drinks?

**Expected SQL:**
```sql
SELECT DISTINCT i.name, i.description, i.is_allergen
FROM ingredients i
JOIN product_ingredients pi ON i.id = pi.ingredient_id
JOIN products p ON pi.product_id = p.id
WHERE p.name LIKE '%Citrus%' OR p.category LIKE '%citrus%';
```

**Expected result columns:** name, description, is_allergen

---

## Question 3

**Natural language:** Are there active promotions for sparkling beverages?

**Expected SQL:**
```sql
SELECT pr.title, pr.discount_pct, pr.description, pr.expires_at, p.name AS product_name
FROM promotions pr
LEFT JOIN products p ON pr.product_id = p.id
WHERE pr.active = 1
  AND (p.category = 'Sparkling Water' OR pr.description LIKE '%sparkling%');
```

**Expected result columns:** title, discount_pct, description, expires_at, product_name

---

## Question 4

**Natural language:** What should a customer do if an order arrives damaged?

**Expected SQL:**
```sql
SELECT title, content
FROM support_articles
WHERE title LIKE '%damaged%' OR content LIKE '%damaged%'
ORDER BY id;
```

**Expected result columns:** title, content

---

## Question 5

**Natural language:** Which products are available for bulk orders?

**Expected SQL:**
```sql
SELECT id, name, category, price, stock_quantity
FROM products
WHERE is_bulk_available = 1
ORDER BY name;
```

**Expected result columns:** id, name, category, price, stock_quantity

---

## Question 6

**Natural language:** What is the calorie count for energy drinks?

**Expected SQL:**
```sql
SELECT name, calories, is_low_sugar
FROM products
WHERE category = 'Energy Drink'
ORDER BY calories DESC;
```

**Expected result columns:** name, calories, is_low_sugar

---

## Question 7

**Natural language:** Show me all active promotions with their discounts.

**Expected SQL:**
```sql
SELECT pr.title, pr.discount_pct, pr.description, pr.expires_at, p.name AS product_name
FROM promotions pr
LEFT JOIN products p ON pr.product_id = p.id
WHERE pr.active = 1
ORDER BY pr.discount_pct DESC;
```

**Expected result columns:** title, discount_pct, description, expires_at, product_name

---

## Question 8

**Natural language:** What are the ingredients in the Green Detox juice?

**Expected SQL:**
```sql
SELECT i.name, i.description, pi.quantity_mg
FROM ingredients i
JOIN product_ingredients pi ON i.id = pi.ingredient_id
JOIN products p ON pi.product_id = p.id
WHERE p.name = 'Green Detox';
```

**Expected result columns:** name, description, quantity_mg

---

## Question 9

**Natural language:** How do I cancel my subscription?

**Expected SQL:**
```sql
SELECT title, content
FROM support_articles
WHERE title LIKE '%cancel%' OR content LIKE '%cancel%'
ORDER BY id;
```

**Expected result columns:** title, content

---

## Question 10

**Natural language:** What coconut water products does DRINKOO sell?

**Expected SQL:**
```sql
SELECT id, name, description, price, calories, is_low_sugar, stock_quantity
FROM products
WHERE category = 'Coconut Water' OR name LIKE '%Coconut%';
```

**Expected result columns:** id, name, description, price, calories, is_low_sugar, stock_quantity

---

## Text2SQL Evaluation Notes

- The RAG retrieval layer generates SQL from the user's natural-language question.
- Each query above is tested against the seeded SQLite database.
- A query is "correct" if it returns the expected result columns and at least one matching row.
- Threshold: >= 9 out of 10 questions must pass (90% correctness).
- Partial credit: if the query returns the right rows but with extra columns, it is still marked correct.
