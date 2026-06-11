#!/usr/bin/env python3
"""Lightweight PR evaluator for the DRINKOO capstone.

This script is intentionally simple. It does not replace human review, but it
does block obviously incomplete PRs and prints a scorecard aligned to plan.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    points: int
    passed: bool
    detail: str


TEXT_EXTENSIONS = {
    ".css",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".txt",
    ".yaml",
    ".yml",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def files_under(repo: Path, relative: str, suffixes: set[str] | None = None) -> list[Path]:
    root = repo / relative
    if not root.exists():
        return []
    files = [path for path in root.rglob("*") if path.is_file()]
    if suffixes is None:
        return files
    return [path for path in files if path.suffix.lower() in suffixes]


def combined_text(repo: Path, folders: list[str]) -> str:
    chunks: list[str] = []
    for folder in folders:
        for path in files_under(repo, folder):
            if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".env.example"}:
                chunks.append(read_text(path))
    return "\n".join(chunks).lower()


def file_is_filled(path: Path) -> bool:
    if not path.exists():
        return False
    text = read_text(path).strip().lower()
    return bool(text) and "todo" not in text


def count_create_tables(sql_text: str) -> int:
    return len(re.findall(r"\bcreate\s+table\b", sql_text, flags=re.IGNORECASE))


def check_backend(repo: Path) -> Check:
    backend_files = [p for p in files_under(repo, "Backend", {".py"}) if p.name != "__init__.py"]
    text = combined_text(repo, ["Backend"])
    signals = ["fastapi", "router", "openrouter", "openrouter_api_key", "upload", "login", "signup"]
    passed = len(backend_files) > 0 and sum(signal in text for signal in signals) >= 4
    detail = "FastAPI/OpenRouter/auth/upload signals found" if passed else "Backend needs FastAPI app code with OpenRouter, auth, and upload routes"
    return Check("Working Python/FastAPI backend and code quality", 15, passed, detail)


def check_frontend(repo: Path) -> Check:
    frontend_files = files_under(repo, "Frontend", {".html", ".css", ".js"})
    text = combined_text(repo, ["Frontend"])
    signals = ["chat", "login", "signup", "upload", "status"]
    passed = len(frontend_files) >= 2 and sum(signal in text for signal in signals) >= 4
    detail = "Frontend pages/assets cover core flows" if passed else "Frontend needs HTML/CSS/JS for login, chat, upload, and status"
    return Check("Frontend usability and presentation", 15, passed, detail)


def check_database_and_text2sql(repo: Path) -> Check:
    sql_files = files_under(repo, "Database", {".sql"})
    sql_text = "\n".join(read_text(path) for path in sql_files)
    other_text = combined_text(repo, ["Database", "Tests", "Reports"])
    table_count = count_create_tables(sql_text)
    text2sql_signal = "text2sql" in other_text or "text-to-sql" in other_text or "expected sql" in other_text
    passed = table_count >= 6 and text2sql_signal
    detail = f"Found {table_count} CREATE TABLE statements and Text2SQL evidence" if passed else "Need schema SQL with at least six tables and Text2SQL correctness evidence"
    return Check("Database schema, saved SQL, and Text2SQL correctness", 20, passed, detail)


def check_rag_and_prompt(repo: Path) -> Check:
    text = combined_text(repo, ["Backend", "Database", "Reports", "Tests"])
    prompt_path = repo / "prompt.md"
    prompt_text = read_text(prompt_path).lower() if prompt_path.exists() else ""
    rag_signals = ["rag", "retrieval", "retrieved context", "grounded", "context"]
    prompt_signals = ["openrouter", "free model", "system prompt", "unknown", "retrieved context"]
    passed = (
        sum(signal in text for signal in rag_signals) >= 3
        and sum(signal in prompt_text for signal in prompt_signals) >= 4
        and "todo" not in prompt_text
    )
    detail = "RAG evidence and filled OpenRouter prompt found" if passed else "Need grounded RAG implementation evidence and completed prompt.md"
    return Check("RAG chatbot quality, grounding, and OpenRouter prompt quality", 20, passed, detail)


def check_auth_and_upload(repo: Path) -> Check:
    text = combined_text(repo, ["Backend", "Security", "Tests"])
    signals = ["password", "hash", "login", "signup", "protected", "upload", "file size", "content_type"]
    passed = sum(signal in text for signal in signals) >= 6
    detail = "Auth and upload validation signals found" if passed else "Need signup/login, protected routes, password hashing, and safe image upload"
    return Check("Authentication, authorization, and image upload", 10, passed, detail)


def check_tests(repo: Path) -> Check:
    test_files = [p for p in files_under(repo, "Tests", {".py"}) if p.name != "__init__.py"]
    text = combined_text(repo, ["Tests"])
    signals = ["test_", "auth", "chat", "upload", "status", "schema"]
    passed = len(test_files) > 0 and sum(signal in text for signal in signals) >= 4
    detail = "Meaningful test files found" if passed else "Need unit/integration tests for auth, chat, upload, schema, and status"
    return Check("Tests and working application evidence", 10, passed, detail)


def check_adlc(repo: Path) -> Check:
    required = [
        repo / ".github" / "copilot-instructions.md",
        repo / "ADLC" / "ai-scope-statement.md",
        repo / "ADLC" / "prompt-review-checklist.md",
        repo / "ADLC" / "uat-protection.md",
    ]
    filled = sum(file_is_filled(path) for path in required)
    passed = filled == len(required)
    detail = "ADLC/UAT evidence files are completed" if passed else "Complete Copilot instructions and ADLC evidence files; remove TODO placeholders"
    return Check("ADLC, UAT protection, and Copilot workflow evidence", 5, passed, detail)


def check_security_observability(repo: Path) -> Check:
    text = combined_text(repo, ["Security", "Observability", "Reports", "Backend"])
    signals = ["security", "secret", "validation", "status", "health", "log", "prompt injection"]
    passed = sum(signal in text for signal in signals) >= 5
    detail = "Security/status/observability evidence found" if passed else "Need security report, status page, logs, and prompt-injection checks"
    return Check("Security, status page, and basic observability", 5, passed, detail)


def evaluate(repo: Path) -> list[Check]:
    return [
        check_backend(repo),
        check_frontend(repo),
        check_database_and_text2sql(repo),
        check_rag_and_prompt(repo),
        check_auth_and_upload(repo),
        check_tests(repo),
        check_adlc(repo),
        check_security_observability(repo),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a DRINKOO capstone PR.")
    parser.add_argument("--repo", default=".", help="Repository root to evaluate")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum passing score")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    checks = evaluate(repo)
    score = sum(check.points for check in checks if check.passed)
    total = sum(check.points for check in checks)

    print("# DRINKOO PR Evaluation")
    print()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        awarded = check.points if check.passed else 0
        print(f"- {status}: {check.name} ({awarded}/{check.points}) - {check.detail}")
    print()
    print(f"Total score: {score}/{total}")
    print(f"Minimum passing score: {args.min_score}/{total}")

    if score < args.min_score:
        print()
        print("Result: FAIL")
        print("Complete the missing evidence and push another commit to this PR.")
        return 1

    print()
    print("Result: PASS")
    print("This automated check is only a first pass. Human review is still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
