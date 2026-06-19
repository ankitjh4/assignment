# UAT Protection Notes

Use this file to document what must not be broken while building the DRINKOO capstone.

## UAT-Locked Files Or Behaviors

Files or behaviors requiring review before change:

```text
plan.md
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
DRINKOO_Capstone_One_Pager.pdf
Finalized prompt behavior after validation
```

## NEVER_MODIFY List

Copied list for Copilot policy alignment:

```text
plan.md
DRINKOO_Capstone_One_Pager.pdf
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
```

## Required Checks Before PR

- [x] App runs locally.
- [x] Backend routes work.
- [x] Frontend pages work.
- [x] Database schema loads.
- [x] Text2SQL checks pass.
- [x] RAG answers are grounded in DRINKOO data.
- [x] OpenRouter prompt is saved in `prompt.md`.
- [x] Auth and protected routes work.
- [x] Image upload validation works.
- [x] Tests pass.
- [x] Security test report is complete.
- [x] `git diff --stat HEAD` shows only expected changes.

## Notes

Current risk: in-memory token store is sufficient for local learning use but should be replaced with persistent sessions for production deployment.
