"""Configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from repo_doctor.models import RepoDoctorConfig


class ConfigError(ValueError):
    """A human-readable configuration error."""


def load_config(path: Path | None) -> RepoDoctorConfig:
    """Load YAML or JSON configuration; return defaults when no file is supplied."""

    if path is None:
        return RepoDoctorConfig()
    if not path.is_file():
        raise ConfigError(f"Configuration file does not exist: {path}")
    try:
        raw: Any
        with path.open("r", encoding="utf-8") as stream:
            if path.suffix.lower() == ".json":
                raw = json.load(stream)
            elif path.suffix.lower() in {".yaml", ".yml"}:
                raw = yaml.safe_load(stream)
            else:
                raise ConfigError("Configuration extension must be .yaml, .yml or .json")
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ConfigError("Configuration root must be an object")
        return RepoDoctorConfig.model_validate(raw)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValidationError) as exc:
        raise ConfigError(f"Invalid configuration: {exc}") from exc
