"""Demo configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DemoUserConfig:
    user_id: str
    display_name: str
    access_allowed: bool
    enroll_images: list[str]
    pass_photo: Optional[str] = None
    pass_video: Optional[str] = None
    denied_photo: Optional[str] = None
    low_quality_photo: Optional[str] = None


@dataclass(frozen=True)
class DemoThresholds:
    verification_threshold: float = 0.7
    identification_threshold: float = 0.7
    quality_threshold: float = 0.7


@dataclass(frozen=True)
class DemoConfig:
    provider: str
    demo_user: DemoUserConfig
    thresholds: DemoThresholds


def _resolve_path(base_dir: Path, value: str) -> str:
    path = Path(value)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return str(path)


def load_demo_config(config_path: str | Path) -> DemoConfig:
    config_path = Path(config_path)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    base_dir = config_path.parent

    thresholds_data = data.get("thresholds", {})
    thresholds = DemoThresholds(
        verification_threshold=float(
            thresholds_data.get("verification_threshold", 0.7)
        ),
        identification_threshold=float(
            thresholds_data.get("identification_threshold", 0.7)
        ),
        quality_threshold=float(thresholds_data.get("quality_threshold", 0.7)),
    )

    demo_user_data = data["demo_user"]
    enroll_images = [
        _resolve_path(base_dir, item) for item in demo_user_data["enroll_images"]
    ]

    demo_user = DemoUserConfig(
        user_id=demo_user_data["user_id"],
        display_name=demo_user_data.get("display_name", demo_user_data["user_id"]),
        access_allowed=bool(demo_user_data.get("access_allowed", True)),
        enroll_images=enroll_images,
        pass_photo=_resolve_path(base_dir, demo_user_data["pass_photo"])
        if demo_user_data.get("pass_photo")
        else None,
        pass_video=_resolve_path(base_dir, demo_user_data["pass_video"])
        if demo_user_data.get("pass_video")
        else None,
        denied_photo=_resolve_path(base_dir, demo_user_data["denied_photo"])
        if demo_user_data.get("denied_photo")
        else None,
        low_quality_photo=_resolve_path(base_dir, demo_user_data["low_quality_photo"])
        if demo_user_data.get("low_quality_photo")
        else None,
    )

    return DemoConfig(
        provider=data.get("provider", "mock"),
        demo_user=demo_user,
        thresholds=thresholds,
    )


def validate_demo_config(config: DemoConfig) -> list[str]:
    errors: list[str] = []

    if not config.demo_user.user_id:
        errors.append("demo_user.user_id is required")
    if not config.demo_user.enroll_images:
        errors.append("demo_user.enroll_images is required")

    return errors

