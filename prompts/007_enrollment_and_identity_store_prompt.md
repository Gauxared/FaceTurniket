# Prompt - Task 007 Enrollment and Identity Store

Рабочая директория:

```text
D:\Kamenev_solo
```

Выполни только задачу:

```text
tasks/007_enrollment_and_identity_store.md
```

## Что сделать

Добавь слой регистрации пользователей и хранения face templates без реального
ML.

Создай пакет:

```text
src/identity/
```

Рекомендуемые модули:

- `models.py`
- `template_store.py`
- `enrollment.py`
- `matcher.py`

Нужно поддержать:

- `UserProfile`;
- `FaceTemplate`;
- `EnrollmentResult`;
- in-memory template store;
- enrollment через mock recognition/provider;
- `1:1 verification`;
- простой mock `1:N identification`.

## Граница ответственности

- Face provider не решает доступ.
- Identity layer хранит шаблоны и считает match/search result.
- Access module принимает итоговое решение.
- Turnstile module только возвращает команду.
- Event log только записывает событие.

Access module не должен напрямую искать по template store.

## Harness

Добавь или обнови сценарии:

- successful `1:1 verification`;
- failed `1:1 verification` for wrong claimed user;
- successful mock `1:N identification`;
- unknown user in template store;
- duplicate enrollment handled deterministically.

## Ограничения

- Не добавляй DeepFace, InsightFace, OpenCV SFace.
- Не обучай модель.
- Не храни реальные фото.
- Не храни реальные biometric embeddings.
- Не открывай турникет из identity layer.
- Не переноси access decision rules в matcher.

## Тесты

Добавь тесты:

- user profiles and templates;
- adding templates;
- duplicate template behavior;
- `1:1 verification` success/failure;
- `1:N identification` success;
- unknown user/template handling;
- integration with mock recognition pipeline.

## Завершение

Запусти:

```powershell
scripts/check.ps1
```

Обнови `docs/CURRENT_STATE.md` и укажи следующий task:

```text
tasks/008_real_face_provider.md
```

