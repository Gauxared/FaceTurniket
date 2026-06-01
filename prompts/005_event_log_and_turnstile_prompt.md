# Prompt - Task 005 Event Log and Mock Turnstile

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/005_event_log_and_turnstile.md
```

## Что сделать

Реализуй local MVP loop:

```text
recognition -> access decision -> turnstile command -> event log
```

Создай:

- `src/devices/turnstile.py`
- `src/events/event_log.py`

`MockTurnstile`:

- открывается только при `AccessDecision.decision == "allow"`;
- остается закрытым при `deny`, `retry`, `manual_check`;
- возвращает `TurnstileCommand`;
- не знает детали ML.

`EventLog`:

- пишет каждую попытку доступа;
- использует JSONL;
- включает timestamp, user_id, decision, reason, similarity, quality_score,
  turnstile_id, command;
- по умолчанию пишет в gitignored local path, например `reports/events.jsonl`.

## Harness Impact

Обнови harness, чтобы он производил:

- recognition result;
- access decision;
- turnstile command;
- event log entry.

Expected checks должны включать turnstile command, где это практично.

## Ограничения

- Не подключай real hardware.
- Не добавляй external DB.
- Не логируй image bytes, реальные фото или реальные biometric templates.
- В unit-тестах используй temp path для event log.

## Тесты

Добавь тесты:

- turnstile opens only on allow;
- deny does not open;
- retry does not open;
- manual_check does not open;
- event written for every decision;
- JSONL line parses back.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/006_quality_gate_and_capture.md
```

