# Выпуск Repo Doctor

## Одноразовая настройка PyPI

Имя дистрибутива — `repo-doctor-levuskin`. Оно отличается от команды
`repo-doctor`, потому что исходное имя дистрибутива уже занято в PyPI.

1. В PyPI создайте pending Trusted Publisher для проекта `repo-doctor-levuskin`.
2. Укажите владельца `Nikita-Levuskin`, репозиторий `Repo-Doctor`, workflow
   `release.yml` и environment `pypi`.
3. В настройках GitHub создайте environment `pypi`. При необходимости включите ручное
   подтверждение публикации.

Токен PyPI в GitHub Secrets не требуется: workflow получает короткоживущий OIDC-токен.

## Подготовка версии

1. Обновите `version` в `pyproject.toml` и `__version__` в
   `src/repo_doctor/__init__.py`.
2. Добавьте изменения в `CHANGELOG.md`.
3. Выполните локальные проверки из `CONTRIBUTING.md`.
4. Объедините изменения в `main` и дождитесь зелёного workflow `CI`.

## Публикация

Создайте и отправьте аннотированный тег, совпадающий с версией пакета:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

Workflow `Release` проверит совпадение тега и версии, соберёт wheel и sdist, проверит
метаданные, создаст GitHub Release с артефактами и опубликует их в PyPI. Повторно
использовать уже опубликованный номер версии нельзя.
