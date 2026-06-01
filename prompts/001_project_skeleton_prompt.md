# Prompt - Task 001 Project Skeleton

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/001_project_skeleton.md
```

## Что сделать

Создай базовую структуру проекта для solo-agent workflow:

- директории из task-файла;
- `README.md`;
- `scripts/check.ps1`;
- `.gitignore`;
- `.gitkeep` только там, где нужно сохранить пустые директории.

`README.md` должен быть полезной входной точкой проекта и ссылаться на:

- `AGENTS.md`;
- `docs/PROJECT.md`;
- `docs/CURRENT_STATE.md`.

`scripts/check.ps1` должен быть безопасен до появления тестов и harness:

- если тесты есть, запускать `python -m pytest -q`;
- если `harness/run_all.py` есть, запускать `python harness/run_all.py`;
- если чего-то еще нет, печатать понятное сообщение;
- возвращать non-zero code при падении реализованной проверки.

## Ограничения

- Не реализуй face recognition.
- Не реализуй access decision.
- Не добавляй API.
- Не добавляй БД.
- Не добавляй real ML dependencies.

## Завершение

Обнови `docs/CURRENT_STATE.md`:

- skeleton реализован;
- следующий task: `tasks/002_contracts_and_mock_pipeline.md`;
- какие проверки сейчас можно запускать.

В конце запусти доступную проверку. Если `scripts/check.ps1` уже создан,
запусти его.

