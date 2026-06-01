"""Web API package for face recognition system."""

from src.web_api.app import app
from src.web_api.services import RecognitionService

__all__ = ["app", "RecognitionService"]
