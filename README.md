# Repo Doctor

[![CI](https://github.com/Nikita-Levuskin/Repo-Doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/Nikita-Levuskin/Repo-Doctor/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Repo Doctor — учебная CLI-утилита для рекурсивного аудита репозиториев и безопасного
создания недостающих служебных файлов. По умолчанию программа только читает файлы.

## Возможности

- проверка README, лицензии, `.gitignore`, манифеста проекта и CI-конфигурации;
- обнаружение случайно добавленных `.env`, типовых строк секретов и битых локальных ссылок README;
- текстовый и JSON-отчёты с кодом правила, уровнем, путём и способом исправления;
- генерация отсутствующих файлов из Jinja2-шаблонов только с явным `--apply`;
- загрузка правил из YAML или JSON;
- единый интерфейс и адаптеры GitHub Pull Request / GitLab Merge Request;
- mock-тесты HTTP без обращения к реальным аккаунтам.

## Требования

- Python 3.12 или новее;
- Windows, Linux или macOS.

## Установка

После публикации релиза в PyPI:

```bash
pipx install repo-doctor-levuskin
# или
uv tool install repo-doctor-levuskin
```

Имя дистрибутива в PyPI — `repo-doctor-levuskin`, команда после установки —
`repo-doctor`.

Напрямую из GitHub:

```bash
pipx install git+https://github.com/Nikita-Levuskin/Repo-Doctor.git
```

Из локального checkout:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
repo-doctor --version
```

Для разработки:

```bash
python -m pip install -e '.[dev]'
```

## Быстрый старт

```bash
repo-doctor scan .
repo-doctor scan . --format json
repo-doctor check .
repo-doctor fix . --dry-run
repo-doctor fix . --apply
repo-doctor config validate config.example.yaml
```

`check` возвращает код `1`, если найдены нарушения уровня `error`. Ошибки пути или
конфигурации дают код `2`, ошибки провайдера — код `3`.

## Безопасность исправлений

`fix` требует ровно один флаг: `--dry-run` либо `--apply`. Существующие файлы не
перезаписываются без `--overwrite`. Целевой путь проверяется относительно корня, а запись
через символическую ссылку запрещается. Повторный запуск после исправления не создаёт
дубликатов.

```bash
repo-doctor fix ./demo/broken-repository --dry-run
repo-doctor fix ./demo/broken-repository --apply
```

## Конфигурация

Формат показан в [`config.example.yaml`](config.example.yaml). Поддерживаются правила:

- `required-readme`;
- `required-license`;
- `required-gitignore`;
- `required-manifest`;
- `required-ci`;
- `forbidden-env`;
- `suspicious-secret`;
- `readme-local-links`.

Неизвестный идентификатор считается ошибкой конфигурации. Для каждого правила можно
задать `enabled` и переопределить `severity` (`info`, `warning`, `error`).

## GitHub и GitLab

Dry-run не требует токена и не делает сетевой запрос:

```bash
repo-doctor pr . --provider github --owner USER --repository REPO \
  --source-branch repo-doctor-fixes --dry-run
```

Реальный запрос требует явного `--apply` и токена только из переменной окружения:

```bash
export GITHUB_TOKEN='...'
repo-doctor pr . --provider github --owner USER --repository REPO \
  --source-branch repo-doctor-fixes --apply
```

Для GitLab используется `GITLAB_TOKEN`. Команда не создаёт ветку, не выполняет commit или
push: исходная ветка должна уже существовать на сервере. Токен не включается в вывод и
текст ошибок.

## Проверка проекта

```bash
ruff check .
mypy src
pytest --cov=repo_doctor --cov-report=term-missing --cov-fail-under=80
python -m build
python -m twine check dist/*
```

CI выполняет проверки на Linux, macOS и Windows, а также отдельно проверяет Python 3.12
и 3.13. Workflow релиза собирает wheel/sdist, создаёт GitHub Release и публикует пакет
в PyPI через Trusted Publishing. Инструкция сопровождающего —
[`docs/releasing.md`](docs/releasing.md).

Материалы курсового проекта находятся в каталоге [`docs`](docs/requirements.md). Полный
сценарий демонстрации приведён в [`docs/defense/demo-script.md`](docs/defense/demo-script.md).

## Ограничения

- поиск секретов эвристический: возможны ложные срабатывания и пропуски;
- проверяются Markdown-ссылки вида `[...]()` и `![...]()`, но не все конструкции HTML;
- генератор создаёт минимальные универсальные шаблоны и не определяет лицензию проекта;
- API-адаптеры создают только PR/MR из уже опубликованной ветки.

## Лицензия

MIT, см. [`LICENSE`](LICENSE).

Правила участия и сообщения об уязвимостях: [`CONTRIBUTING.md`](CONTRIBUTING.md) и
[`SECURITY.md`](SECURITY.md).
