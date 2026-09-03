from __future__ import annotations

from pathlib import Path

from repo_doctor.fixer import apply_fixes
from repo_doctor.models import RepoDoctorConfig
from repo_doctor.scanner import scan_repository


def test_dry_run_does_not_change_files(tmp_path: Path) -> None:
    config = RepoDoctorConfig()
    report = scan_repository(tmp_path, config)
    before = list(tmp_path.rglob("*"))
    actions = apply_fixes(tmp_path, report, config, apply=False)
    assert before == list(tmp_path.rglob("*"))
    assert actions and all(item.status == "planned" for item in actions)


def test_apply_is_idempotent(tmp_path: Path) -> None:
    config = RepoDoctorConfig.model_validate(
        {"templates": {"project_name": "Sample Project", "license_holder": "Student"}}
    )
    first = apply_fixes(tmp_path, scan_repository(tmp_path, config), config, apply=True)
    snapshots = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    second = apply_fixes(tmp_path, scan_repository(tmp_path, config), config, apply=True)
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert any(item.status == "created" for item in first)
    assert second == []
    assert snapshots == after
    assert "Sample Project" in (tmp_path / "README.md").read_text()


def test_existing_content_is_preserved(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("do not overwrite")
    config = RepoDoctorConfig()
    report = scan_repository(tmp_path, config)
    apply_fixes(tmp_path, report, config, apply=True)
    assert readme.read_text() == "do not overwrite"


def test_symlinked_parent_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-dir"
    outside.mkdir()
    (tmp_path / ".github").symlink_to(outside, target_is_directory=True)
    try:
        config = RepoDoctorConfig()
        report = scan_repository(tmp_path, config)
        try:
            apply_fixes(tmp_path, report, config, apply=True)
        except ValueError as exc:
            assert "leaves repository root" in str(exc) or "symlink" in str(exc)
        else:
            raise AssertionError("symlinked generation path was not rejected")
    finally:
        (tmp_path / ".github").unlink()
        outside.rmdir()
