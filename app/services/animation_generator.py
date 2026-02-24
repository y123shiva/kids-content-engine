# app/services/animation_generator.py

from pathlib import Path
from typing import Dict, Optional
from app.services.animation_service import render_script_to_video

def generate_animation(
    script: Dict,
    visuals_dir: Optional[Path] = None,
) -> str:
    """
    High-level animation generator.
    This is what API / frontend / pipeline should call.
    """
    video_path = render_script_to_video(
        script=script,
        visuals_dir=visuals_dir,
    )
    return video_path
