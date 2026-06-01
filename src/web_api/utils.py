"""Utility functions for web API: image and video processing."""

import base64
import io
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def base64_to_image(base64_str: str) -> np.ndarray:
    """Convert base64 string to numpy array (OpenCV format)."""
    # Remove data:image/* prefix if present
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    image_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def image_to_base64(image: np.ndarray) -> str:
    """Convert numpy array (OpenCV format) to base64 string."""
    _, buffer = cv2.imencode('.jpg', image)
    img_bytes = buffer.tobytes()
    b64_str = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"


def base64_to_video_frames(base64_str: str, max_frames: int = 30) -> List[np.ndarray]:
    """
    Convert base64 video to list of frames.
    
    Returns list of frames up to max_frames.
    """
    # Remove data:video/* prefix if present
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    video_data = base64.b64decode(base64_str)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_data)
        tmp_path = tmp.name
    
    try:
        cap = cv2.VideoCapture(tmp_path)
        frames = []
        frame_count = 0
        
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            frame_count += 1
        
        cap.release()
        return frames
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def draw_quality_info(image: np.ndarray, quality_score: float, blur_score: float,
                      brightness_score: float, yaw: int, pitch: int, roll: int) -> np.ndarray:
    """
    Draw quality information on image.
    
    Shows scores and face angles.
    """
    h, w = image.shape[:2]
    
    # Convert to PIL for better text rendering
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Try to use a better font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    # Background rectangle for text
    text_lines = [
        f"Quality: {quality_score:.2f}",
        f"Blur: {blur_score:.2f}",
        f"Brightness: {brightness_score:.2f}",
        f"Angles: Y={yaw}° P={pitch}° R={roll}°",
    ]
    
    y_offset = 10
    for line in text_lines:
        # Draw background
        bbox = draw.textbbox((10, y_offset), line, font=font)
        draw.rectangle(bbox, fill=(0, 0, 0, 200))
        # Draw text
        draw.text((10, y_offset), line, fill=(0, 255, 0), font=font)
        y_offset += 25
    
    # Convert back to OpenCV
    image_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return image_cv


def draw_decision(image: np.ndarray, decision: str, similarity: Optional[float] = None) -> np.ndarray:
    """
    Draw access decision on image.
    
    Draws decision badge (ALLOW/DENY/RETRY/MANUAL_CHECK).
    """
    h, w = image.shape[:2]
    
    # Color by decision
    color_map = {
        "allow": (0, 255, 0),      # Green
        "deny": (0, 0, 255),        # Red
        "retry": (0, 165, 255),     # Orange
        "manual_check": (255, 255, 0),  # Cyan
    }
    
    color = color_map.get(decision, (255, 255, 255))
    
    # Draw large decision box
    cv2.rectangle(image, (w - 250, h - 100), (w - 10, h - 10), color, -1)
    cv2.rectangle(image, (w - 250, h - 100), (w - 10, h - 10), (255, 255, 255), 2)
    
    # Put decision text
    cv2.putText(image, decision.upper(), (w - 240, h - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    
    # Put similarity if available
    if similarity is not None:
        cv2.putText(image, f"Sim: {similarity:.2f}", (w - 240, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    
    return image


def create_timeline_visualization(frame_results: List[dict]) -> str:
    """
    Create timeline visualization of video frame processing.
    
    Returns base64-encoded image showing which frames were good/bad/selected.
    """
    timeline_height = 100
    timeline_width = max(800, len(frame_results) * 3)
    
    timeline = np.ones((timeline_height, timeline_width, 3), dtype=np.uint8) * 255
    
    frame_width = timeline_width // len(frame_results)
    
    for i, result in enumerate(frame_results):
        x_start = i * frame_width
        x_end = x_start + frame_width
        
        # Color by quality
        if result.get("selected"):
            color = (0, 255, 0)  # Green - selected
        elif result.get("face_detected") and result.get("quality_score", 0) > 0.7:
            color = (0, 255, 255)  # Yellow - good quality
        elif result.get("face_detected"):
            color = (0, 165, 255)  # Orange - low quality
        else:
            color = (0, 0, 255)  # Red - no face
        
        cv2.rectangle(timeline, (x_start, 20), (x_end, 80), color, -1)
        cv2.rectangle(timeline, (x_start, 20), (x_end, 80), (0, 0, 0), 1)
        
        # Frame number
        cv2.putText(timeline, str(i), (x_start + 5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    # Add legend
    cv2.putText(timeline, "Green=Selected  Yellow=Good  Orange=Low  Red=No Face",
                (10, timeline_height - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    return image_to_base64(timeline)


def resize_image_for_display(image: np.ndarray, max_width: int = 800,
                             max_height: int = 600) -> np.ndarray:
    """Resize image to fit display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    
    scale = min(max_width / w, max_height / h, 1.0)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
