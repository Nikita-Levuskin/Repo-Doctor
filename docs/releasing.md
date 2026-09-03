# Выпуск Repo Doctor

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
метаданные и создаст GitHub Release с готовыми артефактами. Версию можно установить
напрямую из GitHub:

```bash
pipx install git+https://github.com/Nikita-Levuskin/Repo-Doctor.git@v1.0.0
```

Повторно использовать уже опубликованный номер версии не следует.
