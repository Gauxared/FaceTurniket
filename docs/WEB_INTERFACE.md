# Web Interface for Face Access System

## Overview

Интерактивный веб-интерфейс для тестирования и демонстрации системы распознавания лица.

Позволяет:
- загружать фото для распознавания
- загружать видео для покадровой обработки
- смотреть детальные результаты распознавания и визуализацию
- регистрировать новых пользователей
- проверять решения доступа и журнал событий

## Architecture

### Backend (FastAPI)
Location: `src/web_api/`

- `app.py` - Main FastAPI application and routes
- `schemas.py` - Pydantic models for request/response
- `services.py` - Business logic integration with core pipeline
- `utils.py` - Video processing, image conversion utilities

### Frontend (HTML/CSS/JavaScript)
Location: `static/`

- `index.html` - Main interface
- `css/style.css` - Styling
- `js/main.js` - Client-side logic and API calls

## API Endpoints

### Эндпоинты распознавания

#### POST `/api/recognize`
Recognize a single image.

Request:
```json
{
  "image": "base64_encoded_image_data",
  "mode": "1toN",
  "claimed_user_id": null
}
```

Response:
```json
{
  "success": true,
  "recognition_result": { ... },
  "decision": { ... },
  "similarity": 0.87,
  "quality_score": 0.88,
  "image_display": "base64_encoded_with_annotations"
}
```

#### POST `/api/recognize-video`
Process a video file.

Request:
```json
{
  "video": "base64_video_data",
  "max_frames": 30,
  "mode": "1toN"
}
```

Response:
```json
{
  "success": true,
  "total_frames": 42,
  "processed_frames": 30,
  "results": [
    {
      "frame_index": 0,
      "selected": false,
      "quality_score": 0.45,
      "reason": "low_quality"
    },
    {
      "frame_index": 5,
      "selected": true,
      "quality_score": 0.88,
      "decision": "allow"
    }
  ],
  "final_result": { ... },
  "timeline": "base64_encoded_timeline_visualization"
}
```

### Эндпоинты регистрации

#### POST `/api/enroll`
Enroll a new user.

Request:
```json
{
  "user_id": "user_004",
  "image": "base64_encoded_image_data"
}
```

Response:
```json
{
  "success": true,
  "user_id": "user_004",
  "message": "User enrolled successfully",
  "template_id": "tmpl_001"
}
```

### Info Endpoints

#### GET `/api/users`
List all enrolled users.

Response:
```json
{
  "users": [
    {
      "user_id": "user_001",
      "templates_count": 3,
      "access_allowed": true
    }
  ]
}
```

#### GET `/api/events`
Get recent events.

Response:
```json
{
  "events": [
    {
      "event_id": "evt_001",
      "timestamp": "2026-05-30T10:00:00",
      "user_id": "user_001",
      "decision": "allow",
      "similarity": 0.87
    }
  ]
}
```

### Эндпоинт состояния

#### GET `/api/health`
Check API status.

Response:
```json
{
  "status": "ok",
  "provider": "mock",
  "users_enrolled": 3
}
```

## Frontend Features

### Main Dashboard
- **Вкладка "Распознавание"**
  - Drag-and-drop image upload
  - Photo preview
  - Real-time recognition result display
  - Quality score visualization
  - Decision badge (allow/deny/retry/manual_check)

- **Вкладка "Видео"**
  - Video file upload
  - Frame extraction progress
  - Frame quality timeline
  - Best frame highlight
  - Per-frame results table
  - Final decision display

- **Вкладка "Регистрация"**
  - User ID input
  - Photo upload
  - Enrollment status
  - Template ID display

- **Вкладка "Пользователи"**
  - List of enrolled users
  - Templates per user
  - Access status
  - Delete user button (optional)

- **Вкладка "События"**
  - Recent events log
  - Filters by decision type
  - Export to CSV
  - Real-time updates (WebSocket optional)

### Result Visualization

#### Quality Scores
```
Quality Score:    [████████░] 0.88
Blur Score:       [██████░░░] 0.60
Brightness Score: [███████░░] 0.70
```

#### Face Angles
```
Yaw:   8°   (acceptable)
Pitch: -5°  (acceptable)
Roll:  2°   (acceptable)
```

#### Recognition Details
- Face detected: ✓
- Faces count: 1
- Liveness: ✓ (score: 0.91)
- Match status: matched
- User ID: user_001
- Similarity: 0.87

#### Решение о доступе
```
┌─────────────────────────┐
│   ALLOW ACCESS          │
│ user_matched_and_access │
│       allowed           │
│   Similarity: 0.87      │
└─────────────────────────┘
```

## Integration with Core System

### Pipeline Integration
```
Web API (FastAPI)
    ↓
RecognitionPipeline (existing)
    ↓
FaceRecognitionProvider (Mock or InsightFace)
    ↓
QualityGate (frame selection)
    ↓
IdentityMatcher (1:1/1:N)
    ↓
AccessDecision (allow/deny/etc)
    ↓
EventLog (logging)
```

### No Changes to Core
- Core system (`src/`) remains unchanged
- Web API is a thin adapter layer
- Same contracts and business logic
- Supports both Mock and InsightFace providers

## Dependencies

Add to `requirements.txt`:
```
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6
opencv-python>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
```

## Running the Web Interface

### Development
```powershell
# From project root
python -m uvicorn src.web_api.app:app --reload --host 0.0.0.0 --port 8000
```

Then open browser to `http://localhost:8000`

### Production
```powershell
# Production-grade server
python -m uvicorn src.web_api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

### Unit Tests
Tests for API endpoints, video processing, image conversion utilities.

Location: `tests/test_web_api.py`

### Integration Tests
Tests that verify web API works with core system without breaking existing contracts.

## Future Enhancements

1. **Real-time Camera Feed**
   - WebSocket for live streaming
   - Live quality feedback
   - Real-time decision display

2. **Advanced Visualizations**
   - Face landmarks overlay
   - Heat maps for quality regions
   - Timeline scrubbing for video frames

3. **Admin Panel**
   - User management
   - Access policy configuration
   - Event log export
   - Statistics and metrics

4. **Mobile-Friendly**
   - Responsive design
   - Touch-optimized controls
   - Mobile camera integration

5. **Authentication & Authorization**
   - Login system
   - Role-based access
   - API key management

## Deployment

### Local Development
Runs on `http://localhost:8000` without installation.

### Docker
Optional Dockerfile for containerization.

### Cloud
Can be deployed to cloud platforms (AWS, Azure, GCP).

## File Structure

```
src/
  web_api/
    __init__.py
    app.py              - Main FastAPI app
    schemas.py          - Pydantic models
    services.py         - Core integration
    utils.py            - Video/image processing
  (core system unchanged)

static/
  index.html            - Main UI
  css/
    style.css           - Styling
  js/
    main.js             - Client logic
  images/
    (UI assets)

tests/
  test_web_api.py       - API tests
```


### Frontend Features

- **Финальный сценарий защиты**
  - Показывает обычный поток регистрации и распознавания
  - Демонстрирует allow, deny, retry и manual_check
  - Выводит журнал событий и команду для mock turnstile
