# Шпаргалка к защите

**Цель:** разработать и проверить безопасный Repo Doctor.

**Поток:** CLI → config → scanner/rules → report → fix; отдельно provider interface →
GitHub/GitLab.

**Команды:** `scan`, `check`, `fix --dry-run|--apply`, `pr --provider ... --dry-run|--apply`,
`config validate`, `--help`, `--version`.

**Инварианты:** read-only по умолчанию; нет перезаписи без флага; root containment;
symlink-safe; лимит размера; бинарные не читаются; env tokens; идемпотентность.

**Результаты:** Python 3.12.13; Ruff PASS; mypy PASS; 39/39; coverage 89,72%; sdist/wheel
PASS; clean install PASS; demo 5 → 0; второй apply `[]`.

**Ограничения:** поиск секретов эвристический; шаблоны минимальны; реальный PR/MR и
Windows/Linux не проверялись; оформление предварительно до методички.

