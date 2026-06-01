# Prompt - Task 006 Quality Gate and Capture Flow

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/006_quality_gate_and_capture.md
```

## Что сделать

Добавь deterministic capture flow без реальной камеры:

- `src/camera/mock_camera.py`
- `src/face/quality_gate.py`

Mock camera должен возвращать серию frame descriptors или fixture paths.

Quality gate должен:

- оценивать серию кадров;
- отвергать no face, multiple faces, low quality и spoof indicators, если они
  доступны;
- выбирать лучший acceptable frame;
- возвращать `QualityResult` или capture result с выбранным кадром.

Recognition pipeline должен использовать выбранный кадр.

## Harness Scenarios

Добавь или обнови cases:

- no acceptable frame;
- one good frame among bad frames;
- all frames low quality.

## Ограничения

- Не подключай физическую камеру.
- Не добавляй OpenCV без явной необходимости.
- Не используй реальные личные фото.
- Не допускай `allow` по rejected frame.

## Тесты

Добавь тесты:

- best frame selection;
- all frames rejected;
- low quality leads to retry or deny according to policy;
- recognition pipeline receives selected frame.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/007_enrollment_and_identity_store.md
```
