"""Allow running Repo Doctor as ``python -m repo_doctor``."""

from .cli import app

if __name__ == "__main__":
    app()
