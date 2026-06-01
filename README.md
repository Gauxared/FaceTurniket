# Turnstile Face Access

Локальный прототип системы контроля доступа по фото лица для прохода через турникет.

## Цель

Система получает изображение лица, идентифицирует или верифицирует сотрудника/студента,
проверяет право доступа и принимает решение об открытии турникета.

## Поддерживаемые провайдеры

Система поддерживает выбор face recognition provider через:

- **Mock provider** (по умолчанию) — детерминированный mock для тестов и разработки
- **InsightFace provider** (опционально) — реальное распознавание через InsightFace

Выбор через переменную окружения:

```powershell
$env:FACE_PROVIDER = "mock"  # или "insightface"
```

Или в коде:

```python
from src.face.providers.factory import ProviderFactory

# Mock (default)
provider = ProviderFactory.create()

# InsightFace (требуется pip install insightface onnxruntime)
provider = ProviderFactory.create(provider_name="insightface")
```

## Локальный запуск

```powershell
# Клонировать репозиторий
git clone <repo-url>
cd <repo-dir>

# Создать виртуальное окружение (опционально, но рекомендуется)
python -m venv venv
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Опционально: установить InsightFace для реального распознавания
# pip install insightface onnxruntime
```

## Запуск тестов

```powershell
python -m pytest -q
```

## Запуск harness

```powershell
python harness/run_all.py
```

## Подготовка LFW тестового датасета

Для оценки используется датасет LFW (Labeled Faces in the Wild). Подготовка автоматическая:

```powershell
# Установить scikit-learn
pip install scikit-learn

# Подготовить LFW subset (скачивается ~200 MB при первом запуске)
python tools/prepare_lfw_subset.py
```

Результат:
- `datasets/lfw_subset/Name_Surname/` — все фото человека (enrollment + probe)
- `datasets/lfw_subset/metadata.json` — пользователи, positive_pairs, negative_samples

Параметры:
```powershell
python tools/prepare_lfw_subset.py --min-faces 10 --enroll-per-person 3 --probe-per-person 5 --max-people 50
```

### Оценка на Celebrity Faces Dataset

Для проверки работы InsightFace на кастомном датасете знаменитостей:

```powershell
# Smoke run на 3 людях
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --max-people 3 --enroll-per-person 2 --probe-per-person 2 --threshold 0.7 --provider insightface --report reports/dataset_eval_smoke.json

# Полный evaluation
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --enroll-per-person 3 --probe-per-person 5 --threshold 0.7 --provider insightface --report reports/dataset_eval.json
```

### Оценка на LFW датасете

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset datasets/lfw_subset --enroll-per-person 3 --probe-per-person 5 --threshold 0.7 --provider insightface --report reports/dataset_eval_lfw.json
```

Скрипт оценивает:
- 1:1 verification (positive и negative pairs)
- 1:N identification
- Метрики: True Accept, False Reject, True Reject, False Accept, Top-1 Correct
- Средние similarity для positive и negative pairs

Отчёт сохраняется в JSON (путь через `--report`). Папки `reports/` и `datasets/` исключены из git.

## Запуск веб-интерфейса

Интерактивный веб-интерфейс для тестирования и демонстрации работы системы.

### Развитие

```powershell
# Установить зависимости если не установлены
pip install fastapi uvicorn python-multipart opencv-python pillow

# Запустить веб-сервер
python -m uvicorn src.web_api.app:app --reload --host 0.0.0.0 --port 8000

# Или с переменной окружения для выбора провайдера
$env:FACE_PROVIDER = "mock"  # или "insightface"
python -m uvicorn src.web_api.app:app --reload --host 0.0.0.0 --port 8000
```

Откройте браузер: `http://localhost:8000`

### Возможности веб-интерфейса

- **Вкладка "Распознавание"** — распознавание одного фото
  - Загрузка изображения (drag-and-drop)
  - 1:N identification или 1:1 verification
  - Визуализация качества кадра (blur, brightness, angles)
  - Результат с решением (allow/deny/retry/manual_check)

- **Вкладка "Видео"** — обработка видео кадр за кадром
  - Загрузка видео файла
  - Выбор лучшего кадра через quality gate
  - Timeline визуализация всех кадров
  - Финальное решение по лучшему кадру

- **Вкладка "Регистрация"** — регистрация нового пользователя
  - Ввод user ID
  - Загрузка фото для регистрации
  - Создание template и добавление в базу

- **Вкладка "Пользователи"** — список зарегистрированных пользователей
  - Количество шаблонов per user
  - Статус доступа (allowed/denied)

- **Вкладка "События"** — логирование всех событий доступа
  - Недавние события (decision, user_id, similarity, quality)
  - Фильтр по типу решения
  - Экспорт в CSV

### Production

```powershell
# Production-ready запуск с несколькими workers
python -m uvicorn src.web_api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Проверка всего

```powershell
scripts/check.ps1
```

## Документация

- [AGENTS.md](AGENTS.md) — правила разработки для AI-агента
- [docs/PROJECT.md](docs/PROJECT.md) — описание проекта
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — текущее состояние
- [docs/WEB_INTERFACE.md](docs/WEB_INTERFACE.md) — документация веб-интерфейса
- [docs/WEB_QUICK_START.md](docs/WEB_QUICK_START.md) — быстрый старт веб-интерфейса
- [WEB_INTERFACE_REPORT.md](WEB_INTERFACE_REPORT.md) — отчет о реализации веб-интерфейса

## Сценарий для защиты

Интерфейс и сценарий демонстрации работают на русском языке.

Основной поток в web UI:
1. Зарегистрировать пользователя во вкладке `Регистрация`.
2. Проверить, что пользователь появился во вкладке `Пользователи`.
3. Загрузить фото или видео во вкладке `Распознавание` / `Видео`.
4. Показать решение, команду для турникета и запись в `События`.

Локальные helper-скрипты в `demo/` и `scripts/prepare_demo.py` остаются
дополнительными утилитами и не нужны для основного сценария.
