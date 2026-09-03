# Итоговый отчёт проверки

## Выполненные команды

```text
python3.12 -m venv work/venv
work/venv/bin/python -m pip install -e '.[dev]'
work/venv/bin/ruff check .
work/venv/bin/mypy src
work/venv/bin/pytest --cov=repo_doctor --cov-report=term-missing --cov-fail-under=80
work/venv/bin/python -m build
work/venv/bin/python -m twine check dist/*
python3.12 -m venv work/clean-venv
work/clean-venv/bin/python -m pip install dist/repo_doctor_levuskin-1.0.0-py3-none-any.whl
work/clean-venv/bin/repo-doctor --version
work/clean-venv/bin/python -m repo_doctor --version
repo-doctor scan work/demo-run
repo-doctor fix work/demo-run --dry-run
repo-doctor fix work/demo-run --apply
repo-doctor scan work/demo-run
repo-doctor fix work/demo-run --apply
```

## Фактические результаты

- Ruff: PASS, без замечаний.
- mypy: PASS, 11 исходных модулей.
- pytest: PASS, 39/39.
- branch coverage: PASS, 88,82% при пороге 80%.
- package build: PASS, sdist и универсальный wheel `py3-none-any`.
- metadata check: PASS для sdist и wheel.
- clean install: PASS, оба entry point вывели `1.0.0`.
- GitHub Actions: PASS, [run 33746025570](https://github.com/Nikita-Levuskin/Repo-Doctor/actions/runs/33746025570);
  тесты и установка wheel подтверждены на Linux, macOS и Windows.
- demo: PASS, 5 исходных нарушений; dry-run без записи; 5 созданных файлов; чистый scan;
  повторный apply — `[]`.

## Не выполнено

- Реальный PR/MR не создавался.
- GitHub/GitLab проверены mock-тестами, но не тестовым аккаунтом.
- Окончательное соответствие методичке невозможно проверить без методички.

## Три прохода контроля

Технический: команды и примеры сверены с CLI, несуществующие функции не описаны.

Редакторский: термины Repo Doctor, правило, нарушение, dry-run, PR/MR употребляются
единообразно; цель, задачи и результаты согласованы.

Формальный: предварительная структура и применимость ГОСТ проверены; окончательные поля,
объём и титульные реквизиты требуют методички. DOCX и PDF постранично проверены после
финального рендеринга: 25 страниц A4, наложений и обрезки не обнаружено; аудит доступности
DOCX не выявил замечаний. PPTX проверен на всех 10 слайдах в LibreOffice и инструментом
контроля переполнений: PASS, переполнений не обнаружено.

Итоговый статус: PASS WITH LIMITATIONS.
