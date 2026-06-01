# Prompt - Task 002 Contracts and Mock Pipeline

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/002_contracts_and_mock_pipeline.md
```

## Что сделать

Реализуй контракты и deterministic mock recognition pipeline.

Создай contract models:

- `QualityResult`
- `LivenessResult`
- `MatchResult`
- `RecognitionResult`
- `AccessDecision`
- `EventLogEntry`
- `TurnstileCommand`

Создай face modules:

- `src/face/providers/base.py`
- `src/face/providers/mock_provider.py`
- `src/face/recognition_pipeline.py`

Mock provider должен возвращать `RecognitionResult` по имени файла:

- `user_001_good.jpg` -> matched `user_001`
- `unknown_001.jpg` -> not found
- `low_quality_001.jpg` -> bad quality
- `multiple_faces_001.jpg` -> multiple faces
- `spoof_001.jpg` -> liveness failed
- unknown filename -> safe not-found or invalid-image result

## Важная граница

Face provider не принимает решение о проходе. Он не возвращает final `allow` или
`deny`, не открывает турникет и не пишет event log.

## Тесты

Добавь тесты для:

- создания контрактов;
- mock provider output;
- recognition pipeline output;
- unknown image scenario;
- provider interface shape.

## Ограничения

- Не подключай DeepFace, InsightFace, OpenCV SFace.
- Не обучай модель.
- Не добавляй API или БД.
- Не делай access decision внутри provider.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Если check script еще не готов, запусти:

```powershell
python -m pytest -q
```

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/003_access_decision.md
```

