"""Typer command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from repo_doctor import __version__
from repo_doctor.config import ConfigError, load_config
from repo_doctor.fixer import apply_fixes
from repo_doctor.models import AuditReport, PullRequestRequest, RepoDoctorConfig
from repo_doctor.providers import GitHubProvider, GitLabProvider, ProviderError
from repo_doctor.reporting import format_json, format_text
from repo_doctor.scanner import ScanError, scan_repository

app = typer.Typer(help="Audit and standardize software repositories.", no_args_is_help=True)
config_app = typer.Typer(help="Configuration operations.")
app.add_typer(config_app, name="config")


def _version(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None, "--version", callback=_version, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """Repo Doctor entry point."""


def _audit(path: Path, config: Path | None) -> tuple[RepoDoctorConfig, AuditReport]:
    try:
        settings = load_config(config)
        return settings, scan_repository(path, settings)
    except (ConfigError, ScanError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Repository path."),
    config: Path | None = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("text", "--format", help="text or json"),
) -> None:
    """Scan a repository and report findings without changing files."""

    _, report = _audit(path, config)
    if output not in {"text", "json"}:
        typer.echo("Error: --format must be text or json", err=True)
        raise typer.Exit(code=2)
    typer.echo(format_json(report) if output == "json" else format_text(report))


@app.command()
def check(
    path: Path = typer.Argument(..., help="Repository path."),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Scan and return exit code 1 when error-level findings exist."""

    _, report = _audit(path, config)
    typer.echo(format_text(report))
    if report.has_errors:
        raise typer.Exit(code=1)


@app.command()
def fix(
    path: Path = typer.Argument(..., help="Repository path."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without writing."),
    apply: bool = typer.Option(False, "--apply", help="Create missing files."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Allow replacing existing targets."),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Generate safe fixes; an explicit mode is required."""

    if dry_run == apply:
        typer.echo("Error: choose exactly one of --dry-run or --apply", err=True)
        raise typer.Exit(code=2)
    settings, report = _audit(path, config)
    try:
        actions = apply_fixes(path, report, settings, apply=apply, overwrite=overwrite)
    except (OSError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(json.dumps([item.model_dump() for item in actions], ensure_ascii=False, indent=2))


@app.command()
def pr(
    path: Path = typer.Argument(..., help="Local repository path (validated, never pushed)."),
    provider: str = typer.Option(..., "--provider", help="github or gitlab"),
    owner: str = typer.Option(..., "--owner"),
    repository: str = typer.Option(..., "--repository"),
    source_branch: str = typer.Option(..., "--source-branch"),
    target_branch: str = typer.Option("main", "--target-branch"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    apply: bool = typer.Option(False, "--apply", help="Actually call the provider API."),
) -> None:
    """Plan or create a provider change request; this command never commits or pushes."""

    if dry_run == apply:
        typer.echo("Error: choose exactly one of --dry-run or --apply", err=True)
        raise typer.Exit(code=2)
    try:
        scan_repository(path, load_config(None))
    except ScanError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    request = PullRequestRequest(
        owner=owner,
        repository=repository,
        source_branch=source_branch,
        target_branch=target_branch,
    )
    if dry_run:
        typer.echo(json.dumps({"provider": provider, "request": request.model_dump()}, indent=2))
        return
    adapters = {"github": GitHubProvider, "gitlab": GitLabProvider}
    adapter = adapters.get(provider)
    if adapter is None:
        typer.echo("Error: --provider must be github or gitlab", err=True)
        raise typer.Exit(code=2)
    try:
        result = adapter().create(request)
    except ProviderError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=3) from exc
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@config_app.command("validate")
def validate_config(file: Path) -> None:
    """Validate YAML or JSON configuration."""

    try:
        settings = load_config(file)
        unknown = sorted(set(settings.rules) - {
            "required-readme", "required-license", "required-gitignore", "required-manifest",
            "required-ci", "forbidden-env", "suspicious-secret", "readme-local-links",
        })
        if unknown:
            raise ConfigError(f"Unknown rules: {', '.join(unknown)}")
    except ConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo("Configuration is valid")


if __name__ == "__main__":
    app()
