# Руководство программиста

## Подготовка среды

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Разработка

Новые правила добавляются функцией сигнатуры `(Path, RepoDoctorConfig) -> list[Violation]`
и регистрируются в `BUILTIN_RULES`. Автоисправимое правило должно иметь безопасную цель в
`RULE_TARGETS` и шаблон в `TEMPLATES`. Нельзя передавать секреты через аргументы или модели.

Провайдер реализует `ChangeRequestProvider.create`. HTTP-ошибки следует переводить в
`ProviderError` без тела ответа, так как оно может содержать конфиденциальные данные.

## Проверки

```bash
ruff check .
mypy src
pytest --cov=repo_doctor --cov-report=term-missing --cov-fail-under=80
python -m build
```

Перед выпуском проверить wheel в отдельном окружении. Реальный PR/MR, commit и push не
входят в автоматическую приёмку.

