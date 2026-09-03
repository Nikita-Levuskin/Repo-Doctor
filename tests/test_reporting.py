from __future__ import annotations

import json

from repo_doctor.models import AuditReport, Severity, Violation
from repo_doctor.reporting import format_json, format_text


def test_text_and_json_reports() -> None:
    report = AuditReport(
        root="/demo",
        violations=[
            Violation(
                rule_id="required-readme",
                severity=Severity.ERROR,
                message="Missing README",
                suggestion="Create README.md",
                auto_fixable=True,
            )
        ],
    )
    assert "ERROR" in format_text(report)
    assert "auto-fix" in format_text(report)
    assert json.loads(format_json(report))["violations"][0]["rule_id"] == "required-readme"


def test_clean_text_report() -> None:
    assert "no violations" in format_text(AuditReport(root="/demo"))
