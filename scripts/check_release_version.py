"""Check that a release tag matches the package version."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def project_version(pyproject: Path) -> str:
    """Return the PEP 621 project version from ``pyproject.toml``."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def main(tag: str) -> int:
    """Validate ``v<version>`` and return a process exit code."""
    expected = f"v{project_version(Path('pyproject.toml'))}"
    if tag != expected:
        print(f"Release tag {tag!r} does not match package version {expected!r}.", file=sys.stderr)
        return 1
    print(f"Release tag {tag!r} matches the package version.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_release_version.py TAG", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
