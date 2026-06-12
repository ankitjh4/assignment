# DRINKOO Rollback Runbook

This runbook describes how to roll back a bad change made during an AI-assisted coding session.

## Trigger signals

Roll back when any of these is true:

- Tests fail on the main branch after a Copilot-assisted change.
- `scripts/evaluate_submission.py --repo assignment --min-score 90` drops below 90.
- `scripts/run_text2sql_eval.py` reports correctness < 90%.
- `scripts/run_rag_eval.py` reports faithfulness < 0.85.
- The status page reports `degraded` for more than 5 minutes.
- Prompt-injection refusal regressions appear in production logs.

## Rollback steps

1. Identify the bad SHA.
   - Look at the chat event logs or `git log --oneline -n 20`.
2. Revert the change.
   - For a single commit: `git revert <sha>`.
   - For a series: `git revert <oldest_sha>^..<newest_sha>`.
3. Re-run the local suite.
   - `pytest -q`.
   - `python scripts/run_text2sql_eval.py`.
   - `python scripts/run_rag_eval.py`.
4. Re-run the PR evaluator.
   - `python scripts/evaluate_submission.py --repo assignment --min-score 90`.
5. Re-deploy the previous build (in a real environment) and watch the dashboards for 15 minutes.
6. Open a post-mortem note in `Reports/ai-sdlc-evidence.md` recording what failed, why, and what was reverted.

## Database considerations

- The DRINKOO SQLite database is built from `Database/schema.sql` and `Database/seed.sql`. To roll back data state:
  - `python scripts/seed_db.py` resets and re-seeds.
- Production deployments using Postgres would require a forward-only migration policy with a separate backup/restore step.

## Secret rotation

- If a key rotation is required during rollback:
  - Update `OPENROUTER_API_KEY` in the deployment secret store.
  - Restart the app.
  - Confirm `/api/status` `components.llm.configured` is `true`.

## UAT-locked files

Never roll back or modify the UAT-locked items in [`ADLC/uat-protection.md`](../ADLC/uat-protection.md) without a human approval.
