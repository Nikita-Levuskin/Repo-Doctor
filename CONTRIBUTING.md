# Contributing

## Локальная разработка

Требуется Python 3.12 или новее.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check .
mypy src
pytest --cov=repo_doctor --cov-fail-under=80
python -m build
python -m twine check dist/*
```

В Windows PowerShell окружение активируется командой
`.venv\Scripts\Activate.ps1`.

## Изменения

- Для нового правила добавьте реализацию, конфигурацию по умолчанию и тесты.
- Не ослабляйте безопасное поведение: запись разрешена только с `--apply`, а dry-run
  не должен изменять файлы или обращаться к API.
- Не включайте токены, `.env`, сборочные артефакты и виртуальные окружения в коммиты.
- Изменения пользовательского поведения опишите в `CHANGELOG.md`.

Pull request должен проходить все задания workflow `CI`.
