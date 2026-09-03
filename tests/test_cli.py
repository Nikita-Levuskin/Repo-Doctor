from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from repo_doctor.cli import app

runner = CliRunner()


def test_help_and_version() -> None:
    assert runner.invoke(app, ["--help"]).exit_code == 0
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert "1.0.0" in version.stdout


def test_scan_check_and_fix(tmp_path: Path) -> None:
    scan = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])
    assert scan.exit_code == 0
    assert "required-readme" in scan.stdout
    assert runner.invoke(app, ["check", str(tmp_path)]).exit_code == 1
    assert runner.invoke(app, ["fix", str(tmp_path)]).exit_code == 2
    dry = runner.invoke(app, ["fix", str(tmp_path), "--dry-run"])
    assert dry.exit_code == 0
    assert not (tmp_path / "README.md").exists()
    applied = runner.invoke(app, ["fix", str(tmp_path), "--apply"])
    assert applied.exit_code == 0
    assert (tmp_path / "README.md").exists()


def test_config_validate_and_pr_dry_run(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("version: 1\n")
    assert runner.invoke(app, ["config", "validate", str(config)]).exit_code == 0
    invalid = tmp_path / "unknown.yaml"
    invalid.write_text("rules:\n  unknown:\n    enabled: true\n")
    assert runner.invoke(app, ["config", "validate", str(invalid)]).exit_code == 2
    result = runner.invoke(
        app,
        [
            "pr", str(tmp_path), "--provider", "github", "--owner", "student",
            "--repository", "demo", "--source-branch", "fixes", "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert '"provider": "github"' in result.stdout


def test_cli_errors(tmp_path: Path) -> None:
    assert runner.invoke(app, ["scan", str(tmp_path), "--format", "xml"]).exit_code == 2
    missing = runner.invoke(app, ["scan", str(tmp_path / "missing")])
    assert missing.exit_code == 2
