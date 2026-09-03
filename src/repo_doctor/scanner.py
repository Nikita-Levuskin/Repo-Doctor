"""Repository scanner orchestration."""

from __future__ import annotations

from pathlib import Path

from repo_doctor.models import AuditReport, RepoDoctorConfig
from repo_doctor.rules import BUILTIN_RULES


class ScanError(ValueError):
    """The requested repository cannot be scanned."""


def resolve_root(path: Path) -> Path:
    """Resolve and validate a repository root."""

    try:
        root = path.expanduser().resolve(strict=True)
    except OSError as exc:
        raise ScanError(f"Path is not accessible: {path}: {exc}") from exc
    if not root.is_dir():
        raise ScanError(f"Repository path is not a directory: {root}")
    return root


def scan_repository(path: Path, config: RepoDoctorConfig) -> AuditReport:
    """Run all enabled rules in deterministic order."""

    root = resolve_root(path)
    unknown = sorted(set(config.rules) - set(BUILTIN_RULES))
    if unknown:
        raise ScanError(f"Unknown rules: {', '.join(unknown)}")
    findings = []
    for rule_id, rule in BUILTIN_RULES.items():
        setting = config.rules.get(rule_id)
        if setting is not None and not setting.enabled:
            continue
        findings.extend(rule(root, config))
    findings.sort(key=lambda item: (item.severity.value, item.rule_id, item.path, item.message))
    return AuditReport(root=str(root), violations=findings)
