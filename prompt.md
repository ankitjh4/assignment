# DRINKOO OpenRouter Prompt

Use this file to store the final prompt used for the DRINKOO RAG chatbot or self-evaluation LLM layer.

You must use your own OpenRouter API key with a free model. Do not paste the API key into this file.

## OpenRouter Model

TODO: Write the exact free OpenRouter model name used.

Example:

```text
openrouter/free-model-name-here
```

## Final System Prompt

TODO: Paste the final system prompt here.

The prompt should tell the model to:

1. Answer only from retrieved DRINKOO context.
2. Say when the answer is not available in the provided data.
3. Avoid inventing product, nutrition, order, or policy details.
4. Keep answers concise and useful.
5. Mention the source table or retrieved context when possible.
6. Treat user-uploaded image details carefully and avoid unsupported claims.

## Final User Prompt Template

TODO: Paste the final user prompt template here.

Include placeholders for:

```text
User question:
Retrieved context:
Relevant SQL or table references:
Image metadata, if any:
```

## Prompt Iterations

Record at least three prompt improvements.

| Version | What Changed | Why It Improved The Answer |
| --- | --- | --- |
| v1 | TODO | TODO |
| v2 | TODO | TODO |
| v3 | TODO | TODO |

## Prompt Test Questions

Test your prompt with at least five DRINKOO questions.

1. TODO
2. TODO
3. TODO
4. TODO
5. TODO

## Notes

TODO: Add notes about hallucination handling, unknown-answer behavior, and how the prompt uses retrieved DRINKOO context.
