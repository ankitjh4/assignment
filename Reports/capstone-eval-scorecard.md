# Capstone Evaluation Scorecard

## Text2SQL Correctness
- Sample question count: 10
- Correct SQL matches: 9
- Text2SQL correctness: 90%

## RAG Groundedness
- Retrieval-aware answer checks: pass
- Faithfulness target: >= 0.85
- Observed faithfulness score (manual eval baseline): 0.87

## Coverage And Tests
- Unit and integration tests implemented for auth, chat, upload, status, schema.

## Evidence Index
- Security: `Reports/security-test-report.md`
- Self-eval: `Reports/self-evaluation.md`
- Text2SQL: `Database/text2sql_checks.md`
- Observability: `Observability/monitoring-notes.md`
