"""Human-readable and JSON report formatting."""

from __future__ import annotations

import json

from repo_doctor.models import AuditReport


def format_text(report: AuditReport) -> str:
    """Render a compact terminal report."""

    if not report.violations:
        return f"Repo Doctor: no violations found in {report.root}"
    lines = [f"Repo Doctor: {len(report.violations)} violation(s) in {report.root}"]
    for item in report.violations:
        fix = " [auto-fix]" if item.auto_fixable else ""
        lines.append(
            f"{item.severity.value.upper():7} {item.rule_id} {item.path}: {item.message}{fix}"
        )
        if item.suggestion:
            lines.append(f"         Fix: {item.suggestion}")
    return "\n".join(lines)


def format_json(report: AuditReport) -> str:
    """Render stable UTF-8 JSON."""

    return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
