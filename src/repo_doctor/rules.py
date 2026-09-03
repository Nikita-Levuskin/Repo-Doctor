"""Built-in repository audit rules."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from pathlib import Path

from repo_doctor.models import RepoDoctorConfig, Severity, Violation, relative_display

Rule = Callable[[Path, RepoDoctorConfig], list[Violation]]
MANIFESTS = ("pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml")
CI_PATHS = (Path(".github/workflows"), Path(".gitlab-ci.yml"))
SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
)
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


def _finding(
    rule_id: str,
    default_severity: Severity,
    config: RepoDoctorConfig,
    message: str,
    path: str,
    suggestion: str | None = None,
    auto_fixable: bool = False,
) -> Violation:
    setting = config.rules.get(rule_id)
    severity = setting.severity if setting and setting.severity else default_severity
    return Violation(
        rule_id=rule_id,
        severity=severity,
        message=message,
        path=path,
        suggestion=suggestion,
        auto_fixable=auto_fixable,
    )


def _required_file(
    root: Path,
    config: RepoDoctorConfig,
    rule_id: str,
    names: tuple[str, ...],
    label: str,
) -> list[Violation]:
    if any((root / name).is_file() for name in names):
        return []
    return [
        _finding(
            rule_id,
            Severity.ERROR,
            config,
            f"Missing {label}",
            ".",
            f"Create {names[0]}",
            True,
        )
    ]


def required_readme(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    return _required_file(root, config, "required-readme", ("README.md", "README.rst"), "README")


def required_license(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    return _required_file(root, config, "required-license", ("LICENSE", "LICENSE.md"), "license")


def required_gitignore(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    return _required_file(root, config, "required-gitignore", (".gitignore",), ".gitignore")


def required_manifest(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    return _required_file(root, config, "required-manifest", MANIFESTS, "project manifest")


def required_ci(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    found = (root / CI_PATHS[1]).is_file()
    workflows = root / CI_PATHS[0]
    found = found or (workflows.is_dir() and any(workflows.glob("*.y*ml")))
    if found:
        return []
    return [
        _finding(
            "required-ci",
            Severity.WARNING,
            config,
            "Missing GitHub Actions or GitLab CI configuration",
            ".",
            "Create .github/workflows/ci.yml",
            True,
        )
    ]


def forbidden_env(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    findings: list[Violation] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in config.scan.exclude]
        for name in files:
            if name == ".env" or name.startswith(".env.") and name != ".env.example":
                path = Path(current, name)
                findings.append(
                    _finding(
                        "forbidden-env",
                        Severity.ERROR,
                        config,
                        "Environment file may contain secrets",
                        relative_display(path, root),
                        "Remove it from version control and add it to .gitignore",
                    )
                )
    return findings


def suspicious_secret(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    findings: list[Violation] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in config.scan.exclude]
        for name in files:
            path = Path(current, name)
            try:
                if path.is_symlink() or path.stat().st_size > config.scan.max_file_size:
                    continue
                data = path.read_bytes()
                if b"\x00" in data:
                    continue
                text = data.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                findings.append(
                    _finding(
                        "suspicious-secret",
                        Severity.ERROR,
                        config,
                        "File contains text resembling a credential",
                        relative_display(path, root),
                        "Remove the secret, rotate it and use an environment variable",
                    )
                )
    return findings


def readme_local_links(root: Path, config: RepoDoctorConfig) -> list[Violation]:
    readme = root / "README.md"
    if not readme.is_file() or readme.is_symlink():
        return []
    try:
        if readme.stat().st_size > config.scan.max_file_size:
            return []
        text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    findings: list[Violation] = []
    for raw_target in LINK_PATTERN.findall(text):
        target = raw_target.strip().split("#", 1)[0].split(" ", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        candidate = (root / target).resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError:
            findings.append(
                _finding(
                    "readme-local-links",
                    Severity.WARNING,
                    config,
                    f"README link leaves repository root: {raw_target}",
                    "README.md",
                    "Use a path inside the repository",
                )
            )
            continue
        if not candidate.exists():
            findings.append(
                _finding(
                    "readme-local-links",
                    Severity.WARNING,
                    config,
                    f"README link target does not exist: {raw_target}",
                    "README.md",
                    "Correct or remove the broken link",
                )
            )
    return findings


BUILTIN_RULES: dict[str, Rule] = {
    "required-readme": required_readme,
    "required-license": required_license,
    "required-gitignore": required_gitignore,
    "required-manifest": required_manifest,
    "required-ci": required_ci,
    "forbidden-env": forbidden_env,
    "suspicious-secret": suspicious_secret,
    "readme-local-links": readme_local_links,
}
