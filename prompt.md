# DRINKOO OpenRouter Prompt

## OpenRouter Model

```text
liquid/lfm-2.5-1.2b-instruct:free
```

Free model available at [openrouter.ai](https://openrouter.ai/models/liquid/lfm-2.5-1.2b-instruct:free).
Set `OPENROUTER_MODEL=liquid/lfm-2.5-1.2b-instruct:free` in your `.env` file (or leave blank to use the default).

## Final System Prompt

```text
You are DRINKOO Assistant, a helpful chatbot for the DRINKOO beverage company.

Answer ONLY using the retrieved DRINKOO context provided below. Follow these rules:

1. If the answer is in the context, give a clear, concise answer and mention which product,
   table, or article your answer comes from.
2. If the answer is NOT in the context, say:
   "I don't have that information in the DRINKOO database. Please contact support@drinkoo.com for help."
3. Never invent product names, prices, ingredients, promotions, or policies that are not in the context.
4. Keep answers short and useful — 1 to 4 sentences.
5. If the user uploads an image, acknowledge it but do not make unsupported claims about the
   image content.
6. Do not answer questions unrelated to DRINKOO products, orders, ingredients, promotions,
   or support policies.
```

## Final User Prompt Template

```text
Retrieved DRINKOO context:
{retrieved_context}

User question: {question}

Image details provided by user (if any): {image_metadata}
```

Placeholders:

```text
User question:       {question}           — the user's natural language question
Retrieved context:   {retrieved_context}  — SQL query results from DRINKOO DB tables
Relevant SQL:        included inline in retrieved_context blocks
Image metadata:      {image_metadata}     — optional user-supplied image description
```

## Prompt Iterations

| Version | What Changed | Why It Improved The Answer |
| --- | --- | --- |
| v1 | Basic prompt: "Answer questions about DRINKOO using the data below." | Initial draft — too vague; model sometimes invented products not in the DB |
| v2 | Added explicit refusal rule: "If the answer is NOT in the context, say you don't have the information." | Eliminated hallucinated product names and prices; model now correctly says "I don't know" |
| v3 | Added source citation rule: "mention which product, table, or article your answer comes from." | Improved groundedness — users can verify which DB entry the answer came from; RAG faithfulness measurably improved |

## Prompt Test Questions

1. **Which DRINKOO products are low sugar?**
   - Expected: Berry Splash Zero, Green Detox, Sparkling Lemon Mint, Coconut Calm, Peach Passion Zero
   - Retrieved context: Products table filtered by `is_low_sugar = 1`

2. **What ingredients are used in the citrus drinks?**
   - Expected: Citric acid, caffeine, vitamin C (from Citrus Burst product_ingredients)
   - Retrieved context: Ingredients joined with product_ingredients and products

3. **Are there active promotions for sparkling beverages?**
   - Expected: "Sparkling Beverages Bundle — 15% off, expires 2026-07-31"
   - Retrieved context: Promotions table filtered by `active = 1`

4. **What should a customer do if an order arrives damaged?**
   - Expected: Take photos within 24 hours, contact support@drinkoo.com with order number and photos
   - Retrieved context: Support articles filtered by keyword "damaged"

5. **Which products are available for bulk orders?**
   - Expected: Citrus Burst, Berry Splash Zero, Tropical Storm, Sparkling Lemon Mint, Blueberry Boost, Coconut Calm, Peach Passion Zero
   - Retrieved context: Products table filtered by `is_bulk_available = 1`

## Notes

### Hallucination Handling
- Temperature is set to 0.2 to reduce creative generation.
- The system prompt explicitly forbids inventing data not in the retrieved context.
- The refusal phrase ("I don't have that information in the DRINKOO database") is tested for
  questions outside the dataset scope.

### Unknown-Answer Behavior
- If the retrieval step returns no matching rows, the context passed to the model is:
  `"No specific context found for this question."` — the model is instructed to refuse and redirect
  to `support@drinkoo.com`.

### How the Prompt Uses Retrieved DRINKOO Context
- The RAG retrieval layer queries 5 tables (products, ingredients + product_ingredients,
  promotions, support_articles, orders) based on keyword routing.
- Retrieved rows are formatted as readable bullet lists before being injected into the user prompt.
- The model sees the actual DB values — not generic beverage knowledge — ensuring grounded answers.
