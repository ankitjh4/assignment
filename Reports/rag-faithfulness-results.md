# DRINKOO RAG Faithfulness Results

Questions: 10
Average faithfulness: 0.931
Threshold: 0.85
Status: PASS

Faithfulness here is a lexical-overlap metric between the grounded answer
(produced from retrieved DRINKOO context) and the retrieved snippets, with a
bonus when the answer contains an inline citation. The metric is deterministic
for CI and the test bank.

## Per-question results

### Which DRINKOO products are low sugar?
- Score: 0.900
- Citations used: ['[support:allergen-info]', '[docs:faq]', '[products:Mint Cooler]', '[docs:policies]', '[products:Citrus Zing]']

> DRINKOO products are produced in facilities that handle cocoa and milk solids. [support:allergen-info] Most DRINKOO products are vegan-friendly. [docs:faq] Mint Cooler is a sparkling herbal drink with mint flavor and low sugar. [products:Mint Cooler]

### What ingredients are in Citrus Zing?
- Score: 0.854
- Citations used: ['[products:Citrus Zing Zero]', '[products:Citrus Zing]', '[docs:faq]', '[support:allergen-info]', '[docs:policies]']

> Citrus Zing Zero is a sparkling citrus drink with lemon-lime flavor and zero sugar. [products:Citrus Zing Zero] Citrus Zing is a sparkling citrus drink with lemon-lime flavor and low sugar. [products:Citrus Zing] The DRINKOO chatbot can answer questions in plain English about products, ingredients, promotions, and policies. [docs:faq]

### Are there active promotions for sparkling beverages?
- Score: 1.000
- Citations used: ['[support:return-policy]', '[promotions:SPARKLE10]', '[support:allergen-info]', '[docs:faq]', '[docs:policies]']

> Opened beverages cannot be returned for food safety reasons. [support:return-policy] Ten percent off all sparkling drinks for the summer season. [promotions:SPARKLE10] Other DRINKOO products are free of common allergens, but always check the label for the latest information. [support:allergen-info]

### What should a customer do if an order arrives damaged?
- Score: 1.000
- Citations used: ['[support:damaged-order]', '[docs:policies]', '[docs:faq]', '[promotions:BULK20]', '[support:allergen-info]']

> What to do if your DRINKOO order arrives damaged. [support:damaged-order] DRINKOO will replace the damaged units free of charge or issue a refund within 5 business days. [docs:policies] # DRINKOO Frequently Asked Questions  ## What is DRINKOO? [docs:faq]

### Which products are available for bulk orders?
- Score: 0.613
- Citations used: ['[support:allergen-info]', '[docs:policies]', '[docs:faq]', '[support:gift-cards]', '[support:return-policy]']

> Other DRINKOO products are free of common allergens, but always check the label for the latest information. [support:allergen-info] Bulk orders may take 5 to 7 business days regardless of zone. [docs:policies] Bulk-eligible products are tagged on the catalog and qualify for the BULK20 promotion when you order 24 or more units. [docs:faq]

### Is there a tea promotion?
- Score: 1.000
- Citations used: ['[products:Green Tea Lite]', '[products:Peach Black Tea]', '[promotions:TEACOZY]', '[promotions:OLDPROMO]', '[promotions:COFFEEHOLIDAY]']

> Green Tea Lite is a still tea drink with green-tea flavor and low sugar. [products:Green Tea Lite] Peach Black Tea is a still tea drink with peach flavor and regular sugar. [products:Peach Black Tea] Tea Comfort Week (TEACOZY). [promotions:TEACOZY]

### What is the refund timeline?
- Score: 1.000
- Citations used: ['[support:refund-timeline]', '[support:damaged-order]', '[docs:faq]', '[docs:policies]', '[support:gift-cards]']

> Refund processing timeline. [support:refund-timeline] DRINKOO will replace the damaged units free of charge or issue a refund within 5 business days. [support:damaged-order] # DRINKOO Frequently Asked Questions  ## What is DRINKOO? [docs:faq]

### Which products contain Ginger Extract?
- Score: 1.000
- Citations used: ['[products:Ginger Kick]', '[support:allergen-info]', '[docs:policies]', '[docs:faq]', '[products:Mint Cooler]']

> Ingredients: Cane Sugar (4.8%), Carbonated Water (90.0%), Ginger Extract (1.2%). [products:Ginger Kick] Products in our cold brew mocha line contain cocoa and milk and should be avoided by people with cocoa or dairy allergies. [support:allergen-info] Products in our cold brew mocha line contain cocoa and milk and should be avoided by people with cocoa or dairy allergies. [docs:policies]

### Tell me about the kids drinks.
- Score: 1.000
- Citations used: ['[docs:faq]', '[promotions:KIDS5]', '[promotions:SPARKLE10]', '[products:Kiddo Mango]', '[products:Kiddo Apple]']

> DRINKOO is a beverage company that makes sparkling and still drinks across citrus, berry, herbal, tea, water, kids, sports, and cold-brew coffee categories. [docs:faq] Five percent off kids drinks family packs. [promotions:KIDS5] Ten percent off all sparkling drinks for the summer season. [promotions:SPARKLE10]

### What ingredients are flagged as allergens?
- Score: 0.944
- Citations used: ['[support:allergen-info]', '[docs:faq]', '[docs:policies]', '[support:damaged-order]', '[support:gift-cards]']

> Other DRINKOO products are free of common allergens, but always check the label for the latest information. [support:allergen-info] # DRINKOO Frequently Asked Questions  ## What is DRINKOO? [docs:faq] ## Allergens DRINKOO products are produced in facilities that also handle cocoa and milk solids. [docs:policies]
