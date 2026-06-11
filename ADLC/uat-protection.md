# UAT Protection Notes

Use this file to document what must not be broken while building the DRINKOO capstone.

## UAT-Locked Files Or Behaviors

TODO: List files, database schemas, tests, prompts, or workflows that should not be changed without review.

```text
TODO
```

## NEVER_MODIFY List

TODO: Copy this list into `.github/copilot-instructions.md`.

```text
TODO
```

## Required Checks Before PR

- [ ] App runs locally.
- [ ] Backend routes work.
- [ ] Frontend pages work.
- [ ] Database schema loads.
- [ ] Text2SQL checks pass.
- [ ] RAG answers are grounded in DRINKOO data.
- [ ] OpenRouter prompt is saved in `prompt.md`.
- [ ] Auth and protected routes work.
- [ ] Image upload validation works.
- [ ] Tests pass.
- [ ] Security test report is complete.
- [ ] `git diff --stat HEAD` shows only expected changes.

## Notes

TODO: Add any UAT risks, decisions, or approvals.
