# DRINKOO OpenRouter Prompt

## OpenRouter Model

```text
meta-llama/llama-3.2-3b-instruct:free
```

This is a free model available on OpenRouter. Set `OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free` in your `.env` file.

## Final System Prompt

```text
You are the DRINKOO customer assistant. Answer questions using ONLY the retrieved context
provided below. If the answer is not found in the retrieved context, say "I don't have that
information in the DRINKOO data." Never invent product names, prices, ingredients, or
policies. When you use retrieved context, mention which product or article you are
referencing. Keep answers concise and helpful. Do not answer questions unrelated to DRINKOO
products, orders, or policies.
```

## Final User Prompt Template

```text
Retrieved context:
{context}

User question:
{question}

Image metadata (if any):
{image_metadata}

Instructions:
- Use only the retrieved context above to answer the question.
- If the context does not contain the answer, respond with: "I don't have that information
  in the DRINKOO data."
- Reference the specific product, article, or promotion from the retrieved context.
- Keep the response under 150 words.
```

## Prompt Iterations

| Version | What Changed | Why It Improved The Answer |
| --- | --- | --- |
| v1 | Basic instruction to answer from context only | Established grounding — stopped the model inventing DRINKOO products |
| v2 | Added explicit "say when answer is unknown" instruction | Prevented hallucinated answers when no context matched; model now returns a clean "I don't have that information" message |
| v3 | Added `temperature=0.2` and 150-word cap in the user prompt template | Reduced verbosity and hallucination; answers became more factual and consistent |

## Prompt Test Questions

1. Which DRINKOO products are low sugar?
   → Expected: Lists products with low `sugar_grams` from products table (e.g. Green Detox Water 0g, Mint Green Tea Cooler 1.5g)

2. What ingredients are used in the citrus drinks?
   → Expected: References Lemon Juice, Citric Acid, Stevia for Citrus Burst; Lemon Juice and Cane Sugar for Classic Lemonade

3. Are there active promotions for sparkling beverages?
   → Expected: Mentions Summer Splash Sale (20% off sparkling) from promotions table

4. What should I do if my order arrives damaged?
   → Expected: References the damaged_orders support article — photo, 48 hours, replacement/refund

5. Which products are available for bulk orders?
   → Expected: Lists products where `is_bulk_available = 1` from seed data

## Notes

### Hallucination Handling

The system prompt explicitly instructs the model to use ONLY the retrieved context. The `temperature=0.2` setting keeps the model close to factual output. Unknown questions (no context found) trigger the fallback: the context string is replaced with "No relevant DRINKOO data was found for this question," which prompts the system instruction to return the unknown-answer message.

### Retrieved Context Format

Retrieved context is formatted as labelled blocks:
- `[Product] Name (category, price, sugar, bulk): description`
- `[Support] Title: content (truncated to 600 chars)`
- `[Promotion] Title: description (discount%, end date)`

This labelling helps the model cite which retrieved context item it is drawing from.

### RAG Faithfulness

The retrieval uses keyword matching against DRINKOO product descriptions, support article content, and active promotions. This ensures answers are grounded in the actual database rather than model knowledge. For the five sample questions above, retrieval consistently surfaces the relevant rows from the seeded data.
