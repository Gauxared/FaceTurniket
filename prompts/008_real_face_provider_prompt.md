# Prompt - Task 008 Optional Real Face Provider

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/008_real_face_provider.md
```

Эта задача выполняется только после стабильных mock pipeline, access decision,
harness, event log, quality gate и identity store.

## Что сделать

Добавь один real face provider через существующий provider/adapter interface:

- `DeepFaceProvider`, или
- `InsightFaceProvider`, или
- `OpenCVSFaceProvider`.

Provider должен:

- реализовать тот же `FaceRecognitionProvider` interface;
- возвращать проектные contracts, а не raw objects ML-библиотеки;
- не менять access decision logic;
- не удалять `MockFaceRecognitionProvider`;
- работать с identity/enrollment layer;
- выбираться через config;
- gracefully fail, если optional dependency не установлена.

Default provider должен остаться mock.

## Ограничения

- Не обучай модель с нуля.
- Не используй gender, age, race, emotion и похожие признаки для access.
- Не храни реальные фото в репозитории.
- Не ломай mock provider или harness.
- Не делай real ML dependency обязательной для обычных тестов.
- Не импортируй optional ML packages на module import time, если это ломает
  пользователей без dependency.

## Тесты

Добавь тесты:

- provider interface stable;
- mock provider still works;
- config selects mock provider;
- config can request real provider;
- missing real provider dependency gives clear error;
- identity store still works with mock provider;
- harness passes with mock provider.

Real provider smoke tests должны быть optional или skipped, если зависимости
нет.

## Документация

Обнови:

- `README.md` с optional install instructions;
- `docs/CURRENT_STATE.md`;
- `docs/PROJECT.md`, если behavior изменился;
- `docs/CONTRACTS.md`, только если public contract изменился.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

В финальном ответе явно напиши, что обычные тесты проходят без real ML
dependencies.

