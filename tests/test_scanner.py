from __future__ import annotations

import os
from pathlib import Path

import pytest

from repo_doctor.models import RepoDoctorConfig
from repo_doctor.scanner import ScanError, scan_repository


def _complete(root: Path) -> None:
    (root / "README.md").write_text("# Demo\n")
    (root / "LICENSE").write_text("MIT\n")
    (root / ".gitignore").write_text(".env\n")
    (root / "pyproject.toml").write_text("[project]\nname='demo'\n")
    workflows = root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI\n")


def test_empty_repository_reports_required_files(tmp_path: Path) -> None:
    report = scan_repository(tmp_path, RepoDoctorConfig())
    ids = {item.rule_id for item in report.violations}
    assert ids >= {
        "required-readme",
        "required-license",
        "required-gitignore",
        "required-manifest",
        "required-ci",
    }
    assert report.has_errors


def test_complete_repository_is_clean(tmp_path: Path) -> None:
    _complete(tmp_path)
    report = scan_repository(tmp_path, RepoDoctorConfig())
    assert report.violations == []
    assert not report.has_errors


def test_partial_repository_and_rule_override(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Partial\n")
    config = RepoDoctorConfig.model_validate(
        {"rules": {"required-license": {"enabled": False}, "required-ci": {"severity": "error"}}}
    )
    report = scan_repository(tmp_path, config)
    ids = {item.rule_id for item in report.violations}
    assert "required-readme" not in ids
    assert "required-license" not in ids
    ci_finding = next(item for item in report.violations if item.rule_id == "required-ci")
    assert ci_finding.severity.value == "error"


def test_unknown_rule_and_unavailable_path(tmp_path: Path) -> None:
    config = RepoDoctorConfig.model_validate({"rules": {"made-up": {"enabled": True}}})
    with pytest.raises(ScanError, match="Unknown rules"):
        scan_repository(tmp_path, config)
    with pytest.raises(ScanError, match="not accessible"):
        scan_repository(tmp_path / "absent", RepoDoctorConfig())
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    with pytest.raises(ScanError, match="not a directory"):
        scan_repository(file_path, RepoDoctorConfig())


def test_env_secret_binary_and_large_file(tmp_path: Path) -> None:
    _complete(tmp_path)
    (tmp_path / ".env").write_text("PASSWORD='super-secret-password'\n")
    (tmp_path / "binary.bin").write_bytes(b"\x00token=abcdefghijklmnopqrstuvwxyz")
    (tmp_path / "large.txt").write_text("token=abcdefghijklmnopqrstuvwxyz")
    config = RepoDoctorConfig.model_validate({"scan": {"max_file_size": 8}})
    report = scan_repository(tmp_path, config)
    ids = [item.rule_id for item in report.violations]
    assert ids.count("forbidden-env") == 1
    assert "suspicious-secret" not in ids


def test_suspicious_secret_is_reported_without_value(tmp_path: Path) -> None:
    _complete(tmp_path)
    value = "abcdefghijklmno123456789"
    (tmp_path / "settings.txt").write_text(f"api_key={value}")
    report = scan_repository(tmp_path, RepoDoctorConfig())
    finding = next(item for item in report.violations if item.rule_id == "suspicious-secret")
    assert value not in finding.message


def test_readme_links(tmp_path: Path) -> None:
    _complete(tmp_path)
    (tmp_path / "README.md").write_text(
        "[ok](LICENSE) [missing](docs/nope.md) [outside](../private.txt) [web](https://example.com)"
    )
    report = scan_repository(tmp_path, RepoDoctorConfig())
    messages = [item.message for item in report.violations if item.rule_id == "readme-local-links"]
    assert len(messages) == 2
    assert any("does not exist" in item for item in messages)
    assert any("leaves repository" in item for item in messages)


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks are unavailable")
def test_symlink_is_not_followed_for_secret_scan(tmp_path: Path) -> None:
    _complete(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside-secret.txt"
    outside.write_text("token=abcdefghijklmnopqrstuvwxyz")
    link = tmp_path / "linked-secret.txt"
    link.symlink_to(outside)
    try:
        report = scan_repository(tmp_path, RepoDoctorConfig())
        assert not any(item.path == link.name for item in report.violations)
    finally:
        outside.unlink(missing_ok=True)


def test_unreadable_file_when_supported(tmp_path: Path) -> None:
    _complete(tmp_path)
    path = tmp_path / "private.txt"
    path.write_text("token=abcdefghijklmnopqrstuvwxyz")
    path.chmod(0)
    try:
        report = scan_repository(tmp_path, RepoDoctorConfig())
        assert report.root == str(tmp_path.resolve())
    finally:
        path.chmod(0o600)
