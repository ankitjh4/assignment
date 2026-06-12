#!/usr/bin/env python3
"""Run the Text2SQL evaluation bank and write Reports/text2sql-results.md."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from Backend.database import init_db_if_needed  # noqa: E402
from Backend.text2sql.generator import generate_sql  # noqa: E402
from Backend.text2sql.runner import row_signature, run_select  # noqa: E402
from Backend.text2sql.validator import validate  # noqa: E402


SAMPLES_PATH = HERE / "Database" / "text2sql_samples.json"
REPORT_PATH = HERE / "Reports" / "text2sql-results.md"


def main() -> int:
    init_db_if_needed()
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples = data["samples"]

    total = len(samples)
    correct = 0
    rows_out = []

    for sample in samples:
        question = sample["question"]
        expected_sql = sample["expected_sql"]
        signature = sample["result_signature"]
        try:
            expected_rows = run_select(expected_sql)
        except Exception as exc:
            rows_out.append({"id": sample["id"], "ok": False, "reason": f"expected_sql_failed: {exc}"})
            continue
        expected_sig = row_signature(expected_rows, signature)

        generated = generate_sql(question)
        validation = validate(generated.sql)
        if not validation.ok:
            rows_out.append({"id": sample["id"], "ok": False, "reason": f"invalid_sql: {validation.issues}"})
            continue
        try:
            actual_rows = run_select(validation.cleaned_sql)
        except Exception as exc:
            rows_out.append({"id": sample["id"], "ok": False, "reason": f"runtime_error: {exc}"})
            continue
        actual_sig = row_signature(actual_rows, signature)
        ok = actual_sig == expected_sig
        if ok:
            correct += 1
        rows_out.append({
            "id": sample["id"],
            "ok": ok,
            "generated_sql": validation.cleaned_sql,
            "used_fallback": generated.used_fallback,
            "rows": len(actual_rows),
        })

    pct = (correct / total * 100) if total else 0
    md = [
        "# DRINKOO Text2SQL Evaluation Results",
        "",
        f"Samples: {total}",
        f"Correct: {correct}",
        f"Correctness: {pct:.1f}%",
        f"Threshold: 90%",
        f"Status: {'PASS' if pct >= 90 else 'FAIL'}",
        "",
        "## Per-sample results",
        "",
    ]
    for r in rows_out:
        md.append(f"- [{ 'PASS' if r['ok'] else 'FAIL' }] `{r['id']}` "
                  + (f"-> {r.get('generated_sql', '')}" if r.get('generated_sql') else f"({r.get('reason', '')})"))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(md), encoding="utf-8")
    print(f"Text2SQL correctness: {pct:.1f}% ({correct}/{total}) -> {REPORT_PATH}")
    return 0 if pct >= 90 else 1


if __name__ == "__main__":
    raise SystemExit(main())
