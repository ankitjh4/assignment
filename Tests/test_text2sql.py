"""Text2SQL correctness regression. Must hit >= 90%."""
from __future__ import annotations

import json
from pathlib import Path

from Backend.text2sql.generator import generate_sql
from Backend.text2sql.runner import row_signature, run_select
from Backend.text2sql.validator import validate


SAMPLES_PATH = Path(__file__).resolve().parent.parent / "Database" / "text2sql_samples.json"


def _score_one(sample: dict) -> bool:
    expected_rows = run_select(sample["expected_sql"])
    expected_sig = row_signature(expected_rows, sample["result_signature"])
    generated = generate_sql(sample["question"])
    validation = validate(generated.sql)
    if not validation.ok:
        return False
    try:
        actual_rows = run_select(validation.cleaned_sql)
    except Exception:
        return False
    actual_sig = row_signature(actual_rows, sample["result_signature"])
    return actual_sig == expected_sig


def test_text2sql_correctness_threshold(client):
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples = data["samples"]
    correct = sum(1 for sample in samples if _score_one(sample))
    total = len(samples)
    pct = correct / total
    assert total >= 12, "Need >= 12 Text2SQL samples"
    assert pct >= 0.90, f"Text2SQL correctness {pct:.2%} below 90% threshold ({correct}/{total})"
