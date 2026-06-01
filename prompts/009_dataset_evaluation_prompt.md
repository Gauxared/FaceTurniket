# Prompt - Task 009 Celebrity Dataset Evaluation

Рабочая директория:

```text
D:\Kamenev_solo
```

Локальный датасет для проверки:

```text
D:\Download\Celebrity Faces Dataset
```

Структура датасета:

```text
Celebrity Faces Dataset/
  Angelina Jolie/
    001_....jpg
    ...
  Brad Pitt/
    ...
```

## Цель

Сделать локальный evaluation/smoke flow на реальных фото из датасета
знаменитостей через InsightFace provider.

Важно: это **не обучение модели**. Это проверка:

- умеет ли provider читать реальные изображения;
- извлекаются ли embeddings;
- насколько работает 1:1 verification;
- насколько работает 1:N identification;
- какие threshold дают приемлемые результаты;
- какие фото не проходят detection/quality.

## Перед началом

Обязательно прочитай:

- `AGENTS.md`
- `docs/PROJECT.md`
- `docs/CONTRACTS.md`
- `docs/CURRENT_STATE.md`
- `tasks/008_real_face_provider.md`

Проверь, что InsightFace установлен в:

```text
D:\Kamenev_solo\.venv
```

Команды проверки:

```powershell
.\.venv\Scripts\python.exe -c "import insightface, onnxruntime; print('ok')"
.\.venv\Scripts\python.exe -m pytest -q
```

## Важное исправление перед dataset evaluation

Сначала проверь `src/face/providers/insightface_provider.py`.

Provider должен корректно принимать:

- путь к изображению `str`;
- `Path`;
- numpy image.

Если на входе путь, нужно загрузить файл через `cv2.imread(...)`.

Если файл не существует или `cv2.imread` вернул `None`, вернуть
`RecognitionResult` с `face_detected=False` и понятной причиной, а не падать.

InsightFace `FaceAnalysis.get(...)` должен получать numpy array, не строку.

## Важное исправление embedding flow

Сейчас mock identity layer может использовать deterministic mock embeddings.
Для dataset evaluation нужно добавить способ работать с реальными embeddings,
не ломая mock flow.

Сделай минимально и аккуратно:

- не удаляй mock embeddings;
- не меняй default provider;
- добавь поле/механизм для передачи embedding из InsightFace provider в
  identity/enrollment/matcher;
- если public contract меняется, обнови `docs/CONTRACTS.md` и тесты.

Варианты:

1. Добавить `embedding: Optional[list[float]]` в `MatchResult` или
   `RecognitionResult`.
2. Или добавить отдельный `EmbeddingResult`/`FaceTemplate` flow.

Выбери самый простой вариант, который не ломает существующие тесты.

## Что реализовать

Создай script:

```text
scripts/evaluate_dataset.py
```

Script должен:

1. Принимать путь к датасету:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset"
```

2. Поддерживать параметры:

```text
--max-people
--enroll-per-person
--probe-per-person
--threshold
--provider insightface
--report reports/dataset_eval.json
```

3. Для каждого человека:

- выбрать `enroll-per-person` фото для enrollment/gallery;
- выбрать `probe-per-person` фото для проверки;
- не копировать фото в репозиторий;
- хранить в отчёте только пути, user_id/person name, scores и статусы.

4. Выполнить:

- 1:1 verification: probe photo против правильного claimed user;
- negative 1:1 verification: probe photo против неправильного claimed user;
- 1:N identification: probe photo против всех enrolled templates.

5. Посчитать метрики:

- total people;
- enrolled templates;
- probe images;
- detection failures;
- quality failures;
- 1:1 true accept;
- 1:1 false reject;
- 1:1 true reject;
- 1:1 false accept;
- 1:N top1 correct;
- 1:N not found;
- ambiguous;
- average similarity for positive pairs;
- average similarity for negative pairs.

6. Сохранить JSON report в:

```text
reports/dataset_eval.json
```

7. Напечатать короткий summary в консоль.

## Ограничения

- Не обучай модель.
- Не добавляй реальные фото в репозиторий.
- Не копируй датасет в проект.
- Не коммить `reports/dataset_eval.json`.
- Не используй gender, age, race, emotion для access decision.
- Не делай InsightFace обязательным для обычных pytest/harness.
- Mock provider должен остаться default.
- Harness должен продолжать работать на mock provider.

## Тесты

Добавь тесты без реальных фото:

- dataset scanner на временной структуре папок;
- split enrollment/probe deterministic;
- metrics aggregation;
- JSON report writer;
- provider path loading error for missing image;
- existing mock tests still pass.

Если тесты для InsightFace требуют реальные зависимости или изображения,
пометь их optional/skip.

## Команды проверки

Обычные проверки:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe harness\run_all.py
```

Dataset smoke run на малом объёме:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --max-people 3 --enroll-per-person 2 --probe-per-person 2 --threshold 0.7 --provider insightface --report reports/dataset_eval_smoke.json
```

Если smoke run проходит, можно запустить шире:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --enroll-per-person 3 --probe-per-person 5 --threshold 0.7 --provider insightface --report reports/dataset_eval.json
```

## Документация

Обнови:

- `docs/CURRENT_STATE.md`;
- `README.md` с командой dataset evaluation;
- `.gitignore`, если reports ещё не игнорируются;
- `docs/CONTRACTS.md`, если добавлены embedding-поля.

## Финальный ответ

В финале напиши:

- какие файлы изменены;
- какие проверки прошли;
- сколько людей/фото обработал smoke run;
- где лежит report;
- какие метрики получились;
- какие ограничения остаются.

