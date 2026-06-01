"""FastAPI web application for face recognition system."""

import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.web_api.schemas import (
    AccessDecisionResponse,
    EnrollRequest,
    EnrollResponse,
    EnrollVideoRequest,
    EnrollVideoResponse,
    EventInfo,
    EventsListResponse,
    HealthResponse,
    RecognizeRequest,
    RecognizeResponse,
    RecognizeVideoRequest,
    RecognizeVideoResponse,
    RecognitionResultResponse,
    UserInfo,
    UsersListResponse,
    VideoFrame,
)
from src.web_api.services import RecognitionService
from src.web_api.utils import (
    base64_to_image,
    base64_to_video_frames,
    create_timeline_visualization,
    draw_decision,
    draw_quality_info,
    image_to_base64,
    resize_image_for_display,
)


# Initialize FastAPI
app = FastAPI(
    title="Face Access Control System",
    description="Web interface for testing and demonstrating face recognition",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get provider from environment or default to mock
PROVIDER_NAME = os.getenv("FACE_PROVIDER", "mock")

# Initialize service
service = RecognitionService(provider_name=PROVIDER_NAME)

# Get repo root
repo_root = Path(__file__).parent.parent.parent.resolve()
static_dir = repo_root / "static"

# Mount static files if they exist
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================================
# HTML UI Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main HTML UI."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    
    # Fallback HTML if file not found
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Access Control System</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div id="app">Loading...</div>
        <script src="/static/js/main.js"></script>
    </body>
    </html>
    """


# ============================================================================
# Recognition Endpoints
# ============================================================================

@app.post("/api/recognize", response_model=RecognizeResponse)
async def recognize_image(request: RecognizeRequest):
    """Recognize a single image."""
    try:
        # Convert base64 to image
        image = base64_to_image(request.image)
        if image is None:
            raise ValueError("Could not decode image")
        
        # Process image
        recognition, additional_data = service.recognize_image(
            image, mode=request.mode, claimed_user_id=request.claimed_user_id
        )
        
        # Prepare response
        recognition_response = RecognitionResultResponse(
            face_detected=recognition.face_detected,
            faces_count=recognition.faces_count,
            quality_score=recognition.quality.quality_score,
            blur_score=recognition.quality.blur_score,
            brightness_score=recognition.quality.brightness_score,
            yaw_angle=recognition.quality.yaw_angle,
            pitch_angle=recognition.quality.pitch_angle,
            roll_angle=recognition.quality.roll_angle,
            liveness_is_live=recognition.liveness.is_live,
            liveness_score=recognition.liveness.score,
            match_status=recognition.match.status,
            match_user_id=recognition.match.user_id,
            similarity=recognition.match.similarity,
        )
        
        decision = additional_data["decision"]
        decision_response = AccessDecisionResponse(
            decision=decision.decision,
            reason=decision.reason,
            user_id=decision.user_id,
        )
        
        # Draw annotations on image
        display_image = image.copy()
        display_image = draw_quality_info(
            display_image,
            recognition.quality.quality_score,
            recognition.quality.blur_score,
            recognition.quality.brightness_score,
            recognition.quality.yaw_angle,
            recognition.quality.pitch_angle,
            recognition.quality.roll_angle,
        )
        display_image = draw_decision(
            display_image,
            decision.decision,
            recognition.match.similarity,
        )
        
        display_image = resize_image_for_display(display_image)
        image_base64 = image_to_base64(display_image)
        
        return RecognizeResponse(
            success=True,
            recognition_result=recognition_response,
            decision=decision_response,
            similarity=additional_data["similarity"],
            quality_score=additional_data["quality_score"],
            image_display=image_base64,
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/recognize-video", response_model=RecognizeVideoResponse)
async def recognize_video(request: RecognizeVideoRequest):
    """Recognize a video file."""
    try:
        # Convert base64 to frames
        frames = base64_to_video_frames(request.video, max_frames=request.max_frames)
        if not frames:
            raise ValueError("Could not decode video or no frames extracted")
        
        # Process video
        frame_results, best_recognition, final_data = service.recognize_video(
            frames,
            max_frames=request.max_frames,
            mode=request.mode,
            claimed_user_id=request.claimed_user_id,
        )
        
        # Prepare frame responses
        video_frames = [
            VideoFrame(
                frame_index=result["frame_index"],
                selected=result["selected"],
                quality_score=result["quality_score"],
                blur_score=result["blur_score"],
                brightness_score=result["brightness_score"],
                face_detected=result["face_detected"],
                faces_count=result["faces_count"],
                reason=result.get("reason"),
            )
            for result in frame_results
        ]
        
        # Prepare final result
        final_result = None
        final_decision = None
        if best_recognition:
            final_result = RecognitionResultResponse(
                face_detected=best_recognition.face_detected,
                faces_count=best_recognition.faces_count,
                quality_score=best_recognition.quality.quality_score,
                blur_score=best_recognition.quality.blur_score,
                brightness_score=best_recognition.quality.brightness_score,
                yaw_angle=best_recognition.quality.yaw_angle,
                pitch_angle=best_recognition.quality.pitch_angle,
                roll_angle=best_recognition.quality.roll_angle,
                liveness_is_live=best_recognition.liveness.is_live,
                liveness_score=best_recognition.liveness.score,
                match_status=best_recognition.match.status,
                match_user_id=best_recognition.match.user_id,
                similarity=best_recognition.match.similarity,
            )
            
            decision = final_data.get("decision")
            if decision:
                final_decision = AccessDecisionResponse(
                    decision=decision.decision,
                    reason=decision.reason,
                    user_id=decision.user_id,
                )
        
        # Create timeline visualization
        timeline_base64 = create_timeline_visualization(frame_results)
        
        return RecognizeVideoResponse(
            success=True,
            total_frames=len(frames),
            processed_frames=len(frame_results),
            results=video_frames,
            final_result=final_result,
            final_decision=final_decision,
            best_frame_index=next(
                (r["frame_index"] for r in frame_results if r["selected"]), None
            ),
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Enrollment Endpoints
# ============================================================================

@app.post("/api/enroll", response_model=EnrollResponse)
async def enroll_user(request: EnrollRequest):
    """Enroll a new user."""
    try:
        payload_images = []
        if request.images:
            payload_images.extend(request.images)
        if request.image:
            payload_images.append(request.image)
        if not payload_images:
            raise ValueError("image or images is required")

        decoded_images = []
        for encoded in payload_images:
            image = base64_to_image(encoded)
            if image is None:
                raise ValueError("Could not decode image")
            decoded_images.append(image)

        result = service.enroll_user_images(
            images=decoded_images,
            full_name=request.full_name,
            user_id=request.user_id,
        )

        return EnrollResponse(
            success=result["success"],
            user_id=result["user_id"],
            full_name=result.get("full_name"),
            template_id=result["template_ids"][0] if result["template_ids"] else None,
            template_ids=result["template_ids"],
            enrolled_images=result["enrolled_images"],
            message=result["message"],
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/enroll-video", response_model=EnrollVideoResponse)
async def enroll_user_video(request: EnrollVideoRequest):
    """Enroll a user from a short video."""
    try:
        if not request.user_id and not request.full_name:
            raise ValueError("full_name or user_id is required")

        frames = base64_to_video_frames(request.video, max_frames=request.max_frames)
        if not frames:
            raise ValueError("Could not decode video or no frames extracted")

        result = service.enroll_user_video(
            user_id=request.user_id,
            frames=frames,
            full_name=request.full_name,
            max_templates=request.max_templates,
        )
        return EnrollVideoResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Info Endpoints
# ============================================================================

@app.get("/api/users", response_model=UsersListResponse)
async def get_users():
    """Get list of enrolled users."""
    try:
        users = service.get_enrolled_users()
        return UsersListResponse(users=users)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events", response_model=EventsListResponse)
async def get_events(limit: int = 50):
    """Get recent events."""
    try:
        events_data = service.get_recent_events(limit=limit)
        events = []
        
        # Convert to EventInfo objects
        for evt in events_data:
            events.append(EventInfo(
                event_id=evt.get("event_id", "unknown"),
                timestamp=evt.get("timestamp", ""),
                user_id=evt.get("user_id"),
                decision=evt.get("decision", "unknown"),
                reason=evt.get("reason", ""),
                similarity=evt.get("similarity"),
                quality_score=evt.get("quality_score"),
            ))
        
        return EventsListResponse(
            events=events,
            total_count=len(events),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    try:
        status = service.get_health_status()
        return HealthResponse(
            status=status["status"],
            provider=status["provider"],
            users_enrolled=status["users_enrolled"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Error Handling
# ============================================================================

from fastapi.responses import JSONResponse


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
