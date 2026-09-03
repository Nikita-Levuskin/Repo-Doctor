from __future__ import annotations

from pathlib import Path

import pytest

from repo_doctor.fixer import apply_fixes
from repo_doctor.models import RepoDoctorConfig
from repo_doctor.scanner import scan_repository


@pytest.mark.integration
def test_empty_to_standardized_repository(tmp_path: Path) -> None:
    config = RepoDoctorConfig.model_validate({"templates": {"license_holder": "Test Student"}})
    initial = scan_repository(tmp_path, config)
    assert initial.has_errors
    apply_fixes(tmp_path, initial, config, apply=True)
    final = scan_repository(tmp_path, config)
    assert final.violations == []
