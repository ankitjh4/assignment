"""SQL safety validator: SELECT-only, single statement, allowlist of tables/columns."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Set

import sqlglot
from sqlglot import exp

from .schema_card import ALLOWED_TABLES


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "TRUNCATE",
    "REPLACE",
    "CREATE",
    "MERGE",
    "GRANT",
    "REVOKE",
}


@dataclass
class ValidationResult:
    ok: bool
    cleaned_sql: str
    issues: List[str]


def _split_statements(sql: str) -> List[str]:
    parts = [stmt.strip() for stmt in re.split(r";\s*", sql) if stmt.strip()]
    return parts


def _collect_used_tables(parsed: exp.Expression) -> Set[str]:
    return {table.name.lower() for table in parsed.find_all(exp.Table) if table.name}


def _collect_used_columns(parsed: exp.Expression) -> Set[str]:
    return {col.name.lower() for col in parsed.find_all(exp.Column) if col.name}


def _collect_select_aliases(parsed: exp.Expression) -> Set[str]:
    aliases: Set[str] = set()
    for select in parsed.find_all(exp.Select):
        for expression in select.expressions or []:
            if isinstance(expression, exp.Alias) and expression.alias:
                aliases.add(expression.alias.lower())
    return aliases


def validate(sql: str, limit_cap: int = 100) -> ValidationResult:
    issues: List[str] = []
    if not sql or not sql.strip():
        return ValidationResult(False, "", ["empty_sql"])

    statements = _split_statements(sql)
    if len(statements) != 1:
        issues.append("must_be_single_statement")
        return ValidationResult(False, "", issues)

    statement = statements[0]
    upper = statement.upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            issues.append(f"forbidden_keyword:{kw}")
    if issues:
        return ValidationResult(False, "", issues)

    try:
        parsed = sqlglot.parse_one(statement, read="sqlite")
    except Exception as exc:
        return ValidationResult(False, "", [f"parse_error:{exc}"])

    if not isinstance(parsed, exp.Select):
        return ValidationResult(False, "", ["must_be_select"])

    used_tables = _collect_used_tables(parsed)
    allowed_table_names = {name.lower() for name in ALLOWED_TABLES.keys()}
    unknown_tables = used_tables - allowed_table_names
    if unknown_tables:
        issues.append(f"unknown_tables:{sorted(unknown_tables)}")

    allowed_columns = {col.lower() for cols in ALLOWED_TABLES.values() for col in cols}
    allowed_columns |= _collect_select_aliases(parsed)
    used_columns = _collect_used_columns(parsed)
    suspicious_columns = used_columns - allowed_columns
    if suspicious_columns:
        issues.append(f"unknown_columns:{sorted(suspicious_columns)}")

    if issues:
        return ValidationResult(False, "", issues)

    existing_limit = parsed.args.get("limit")
    if existing_limit is None:
        parsed.set("limit", exp.Limit(expression=exp.Literal.number(limit_cap)))
    else:
        try:
            current = int(str(existing_limit.expression))
            if current > limit_cap:
                parsed.set("limit", exp.Limit(expression=exp.Literal.number(limit_cap)))
        except (ValueError, AttributeError):
            parsed.set("limit", exp.Limit(expression=exp.Literal.number(limit_cap)))

    return ValidationResult(True, parsed.sql(dialect="sqlite"), [])
