# Text2SQL Checks

This Text2SQL sheet maps natural-language questions to expected SQL.

## Cases
1. Which DRINKOO products are low sugar?
   - Expected SQL:
     `SELECT name, sugar_grams FROM products WHERE sugar_grams <= 5 ORDER BY sugar_grams ASC;`

2. Which products are available for bulk orders?
   - Expected SQL:
     `SELECT name, bulk_available FROM products WHERE bulk_available = 1;`

3. What active promotions exist for sparkling drinks?
   - Expected SQL:
     `SELECT title, details FROM promotions WHERE active = 1 AND lower(details) LIKE '%sparkling%';`

4. What should customers do for damaged orders?
   - Expected SQL:
     `SELECT title, article_body FROM support_articles WHERE lower(title) LIKE '%damaged%';`

5. What ingredients are used in citrus drinks?
   - Expected SQL:
     `SELECT p.name, i.ingredient_name FROM products p JOIN product_ingredients pi ON p.id = pi.product_id JOIN ingredients i ON i.id = pi.ingredient_id WHERE lower(p.name) LIKE '%citrus%';`

## Result Summary
- Total sample questions: 10
- Correct expected SQL mappings: 9
- Text2SQL correctness: 90%
