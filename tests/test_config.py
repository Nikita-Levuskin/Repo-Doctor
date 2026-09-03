from __future__ import annotations

import json
from pathlib import Path

import pytest

from repo_doctor.config import ConfigError, load_config


def test_default_config() -> None:
    config = load_config(None)
    assert config.version == 1
    assert config.scan.max_file_size > 0


@pytest.mark.parametrize(
    ("name", "content"),
    [("broken.yaml", "rules: ["), ("broken.json", '{"version":')],
)
def test_broken_config(tmp_path: Path, name: str, content: str) -> None:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigError, match="Invalid configuration"):
        load_config(path)


def test_json_and_yaml_configs(tmp_path: Path) -> None:
    json_path = tmp_path / "config.json"
    json_path.write_text(json.dumps({"rules": {"required-ci": {"enabled": False}}}))
    yaml_path = tmp_path / "config.yml"
    yaml_path.write_text("scan:\n  max_file_size: 128\n", encoding="utf-8")
    assert not load_config(json_path).rules["required-ci"].enabled
    assert load_config(yaml_path).scan.max_file_size == 128


def test_invalid_extension_and_missing_file(tmp_path: Path) -> None:
    wrong = tmp_path / "config.txt"
    wrong.write_text("{}")
    with pytest.raises(ConfigError, match="extension"):
        load_config(wrong)
    with pytest.raises(ConfigError, match="does not exist"):
        load_config(tmp_path / "missing.yml")


def test_non_object_config(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("- one\n- two\n")
    with pytest.raises(ConfigError, match="root must be an object"):
        load_config(path)
