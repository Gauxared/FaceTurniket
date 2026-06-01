# Prompt - Task 003 Access Decision

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/003_access_decision.md
```

## Что сделать

Реализуй business access decision:

- `src/access/decision.py`
- `src/access/policies.py`

Основная функция должна принимать `RecognitionResult` и возвращать
`AccessDecision`.

## Правила в нужном приоритете

1. face not detected -> `deny`
2. multiple faces -> `deny`
3. low quality -> `retry`
4. liveness failed -> `deny`
5. match not found -> `deny`
6. ambiguous match -> `manual_check` или `deny`
7. similarity below threshold -> `deny`
8. user not allowed -> `deny`
9. matched and access allowed -> `allow`

Если в текущем recognition contract еще нет прав доступа, добавь маленький
локальный mock policy/user registry в `src/access/policies.py`.

## Ограничения

- Не добавляй ML logic в access module.
- Не импортируй ML-библиотеки.
- Не открывай турникет из `decision.py`.
- Не пиши event log из `decision.py`.
- Не мутируй `RecognitionResult`.

## Тесты

Добавь тесты для всех правил:

- allow matched user with access;
- deny unknown user;
- retry low quality;
- deny spoof attempt;
- deny user without access;
- deny multiple faces;
- deny face not detected;
- deny low similarity;
- manual_check или deny ambiguous match.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/004_harness.md
```

