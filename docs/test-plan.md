# Трассировка требований к тестам

| Требование | Проверка |
|---|---|
| FR-01, FR-02 | `test_empty_repository_reports_required_files`, `test_complete_repository_is_clean` |
| FR-03 | `test_env_secret_binary_and_large_file`, `test_suspicious_secret_is_reported_without_value`, `test_readme_links` |
| FR-04, FR-05 | `test_text_and_json_reports` |
| FR-06, NFR-02, NFR-06 | `test_dry_run_does_not_change_files`, `test_apply_is_idempotent`, `test_existing_content_is_preserved` |
| FR-07 | `test_json_and_yaml_configs`, `test_broken_config`, `test_unknown_rule_and_unavailable_path` |
| FR-08, NFR-05, NFR-07 | все тесты `test_providers.py`, `test_config_validate_and_pr_dry_run` |
| NFR-03 | `test_symlink_is_not_followed_for_secret_scan`, `test_symlinked_parent_is_rejected` |
| NFR-04 | `test_env_secret_binary_and_large_file` |
| Интеграционный сценарий | `test_empty_to_standardized_repository` |

Проверка Windows/Linux/macOS выполняется на уровне `pathlib`, отсутствия жёстких
разделителей пути в ядре и CI-совместимого кода. Фактический локальный запуск в этой
работе выполняется на macOS; кроссплатформенный CI для трёх ОС не заявлен как пройденный.

