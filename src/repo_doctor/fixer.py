"""Safe, idempotent generation of missing repository files."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, StrictUndefined

from repo_doctor.models import AuditReport, FixAction, RepoDoctorConfig
from repo_doctor.scanner import resolve_root
from repo_doctor.templates import TEMPLATES

RULE_TARGETS = {
    "required-readme": "README.md",
    "required-license": "LICENSE",
    "required-gitignore": ".gitignore",
    "required-manifest": "pyproject.toml",
    "required-ci": ".github/workflows/ci.yml",
}


def _safe_target(root: Path, relative: str) -> Path:
    target = (root / relative).resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Generated path leaves repository root: {relative}") from exc
    current = root
    for part in Path(relative).parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Refusing to write through symlink: {current}")
    return target


def apply_fixes(
    path: Path,
    report: AuditReport,
    config: RepoDoctorConfig,
    *,
    apply: bool,
    overwrite: bool = False,
) -> list[FixAction]:
    """Plan or apply automatic fixes reported by the scanner."""

    root = resolve_root(path)
    env = Environment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)
    project_name = config.templates.project_name or root.name
    project_slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-") or "project"
    context = {
        "project_name": project_name,
        "project_slug": project_slug,
        "license_holder": config.templates.license_holder,
        "python_package": config.templates.python_package,
    }
    actions: list[FixAction] = []
    seen: set[str] = set()
    for violation in report.violations:
        relative = RULE_TARGETS.get(violation.rule_id)
        if not violation.auto_fixable or relative is None or relative in seen:
            continue
        seen.add(relative)
        target = _safe_target(root, relative)
        if target.exists() and not overwrite:
            actions.append(FixAction(path=relative, status="skipped", reason="file already exists"))
            continue
        if target.is_symlink():
            actions.append(FixAction(path=relative, status="skipped", reason="target is a symlink"))
            continue
        if not apply:
            actions.append(FixAction(path=relative, status="planned", reason="dry-run"))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered = env.from_string(TEMPLATES[relative]).render(**context)
        target.write_text(rendered, encoding="utf-8", newline="\n")
        actions.append(FixAction(path=relative, status="created", reason="missing file generated"))
    return actions
