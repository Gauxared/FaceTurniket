# Prompt - Task 004 Harness

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/004_harness.md
```

## Что сделать

Создай локальный scenario harness:

- `harness/cases/`
- `harness/fixtures/`
- `harness/run_all.py`

Harness должен:

1. Читать YAML или JSON cases.
2. Запускать recognition pipeline.
3. Запускать access decision.
4. Сравнивать actual с expected.
5. Печатать passed/failed по каждому case.
6. Печатать итоговый summary.
7. Возвращать non-zero exit code при любом failed case.

Если YAML требует новую зависимость, используй JSON или маленький безопасный
parser для ограниченного формата.

## Обязательные сценарии

- `known_user_allowed`
- `unknown_user_denied`
- `low_quality_photo`
- `multiple_faces`
- `spoof_attempt`
- `user_without_access`

Если scope остается маленьким, добавь:

- `no_face`
- `low_similarity`
- `ambiguous_match`

## Ограничения

- Не используй реальные личные фото.
- Не завись от real ML.
- Не завись от внешних сервисов.
- Не делай harness зеленым при malformed case.

## Тесты

Добавь тесты:

- cases загружаются;
- все committed cases проходят;
- временный mismatch case падает понятно;
- CLI возвращает `0`, когда все cases проходят.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Обнови `README.md`, если команда harness еще не описана.

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/005_event_log_and_turnstile.md
```

