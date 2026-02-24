import math
import json
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ===== Project imports =====
from app.services.motion_engine import resolve_motions, apply_motion
# from app.services.audio_alignment import align_phonemes (commented if not ready)

DEFAULT_FPS = 24
DEFAULT_RESOLUTION = (1280, 720)
BACKGROUND_COLOR = (135, 206, 235)  # Sky Blue instead of white

# ==========================
# 🎨 Procedural Asset Fallbacks
# ==========================
def _get_fallback_character(resolution) -> Image.Image:
    """Draws a simple Bibo robot using shapes if no image exists."""
    img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Body
    draw.ellipse([100, 100, 300, 350], fill="#3498db", outline="white", width=5)
    # Eyes
    draw.ellipse([140, 160, 180, 200], fill="white")
    draw.ellipse([220, 160, 260, 200], fill="white")
    # Digital Pupils
    draw.ellipse([155, 175, 165, 185], fill="#2c3e50")
    draw.ellipse([235, 175, 245, 185], fill="#2c3e50")
    return img

def _load_character_sprite(name: str) -> Image.Image:
    path = Path("assets/characters") / f"{name}.png"
    if path.exists():
        return Image.open(path).convert("RGBA")
    return _get_fallback_character((400, 400))

def _load_font(size: int = 42):
    path = Path("assets/fonts/rounded.ttf")
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

# ==========================
# 🎥 Core Frame Renderer
# ==========================
def render_shot_frames(
    title: str,
    scene_number: int,
    narration: str,
    duration: float,
    out_dir: Path,
    fps: int = DEFAULT_FPS,
    resolution: Tuple[int, int] = DEFAULT_RESOLUTION,
    character_name: str = "bibo",
    audio_cues: Optional[List[str]] = None,
):
    width, height = resolution
    total_frames = int(duration * fps)
    out_dir.mkdir(parents=True, exist_ok=True)

    character = _load_character_sprite(character_name)
    font = _load_font()
    motions = resolve_motions(audio_cues or [])

    # Base position (Center Bottom)
    cx = width // 2 - character.width // 2
    cy = height - character.height - 50

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = Image.new("RGBA", resolution, BACKGROUND_COLOR)
        draw = ImageDraw.Draw(frame)

        # 1. Background Logic (Procedural Grass)
        draw.rectangle([0, height-100, width, height], fill="#2ecc71")

        # 2. Subtitles
        draw.text((width // 2, height - 50), narration, font=font, fill="white", anchor="mm")

        # 3. ALGORITHM: Bouncing Motion
        # Apply motion from engine + a constant idle 'float'
        mx, my = cx, cy
        idle_bounce = 15 * math.sin(2 * math.pi * 1.5 * t)
        
        for motion in motions:
            mx, my = apply_motion(motion, t, (mx, my))
        
        # 4. Paste Character
        frame.paste(character, (int(mx), int(my + idle_bounce)), character)

        # 5. Save Frame
        frame.save(out_dir / f"scene_{scene_number}_{frame_idx:04d}.png")

    return out_dir

def render_script_to_video(script: dict, aspect: str = "youtube"):
    """Accepts a dictionary (script) directly from the API."""
    title = script.get("title", "video").replace(" ", "_")
    scenes = script.get("scenes", [])
    
    # Create a unique output folder for frames
    render_id = title.lower()
    frames_base_dir = Path(f"outputs/visuals/{render_id}")
    
    for scene in scenes:
        scene_dir = frames_base_dir / f"scene_{scene['scene_number']}"
        render_shot_frames(
            title=title,
            scene_number=scene["scene_number"],
            narration=scene.get("narration") or scene.get("text", ""),
            duration=scene.get("duration_seconds") or 5.0,
            out_dir=scene_dir,
            audio_cues=scene.get("audio_cues", [])
        )

    # Path to final video
    output_video = Path("outputs/video") / f"{render_id}.mp4"
    output_video.parent.mkdir(parents=True, exist_ok=True)
    
    # Trigger your ffmpeg utility
    # frames_to_video(frames_base_dir, output_video, DEFAULT_FPS)
    
    return str(output_video)