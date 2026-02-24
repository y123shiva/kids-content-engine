from pathlib import Path
from typing import List, Optional, Dict
from mutagen.mp3 import MP3
import re
import logging

from app.services.tts_generator import generate_tts

# =========================================================
# CONFIG
# =========================================================

AUDIO_ROOT = Path("outputs/audio")
VIDEO_ROOT = Path("outputs/video")
VISUALS_ROOT = Path("outputs/visuals")

AUDIO_ROOT.mkdir(parents=True, exist_ok=True)
VIDEO_ROOT.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)

# =========================================================
# UTILITIES
# =========================================================

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def get_audio_duration(path: Path) -> float:
    try:
        audio = MP3(str(path))
        return float(audio.info.length)
    except Exception:
        return 0.0


# =========================================================
# OPTIONAL: SIMPLE TTS ENGINE (REPLACE WITH YOUR PROVIDER)
# =========================================================

def generate_audio_file(text: str, output_path: Path):
    """
    Replace this function with your real TTS engine.
    Example below uses gTTS (Google TTS).
    """
    from gtts import gTTS

    tts = gTTS(text=text, lang="en")
    tts.save(str(output_path))


# =========================================================
# IMAGE ANIMATION
# =========================================================

def animated_image_clip(image_path: Path, duration: float):
    from moviepy.video.VideoClip import ImageClip
    import numpy as np

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    clip = ImageClip(str(image_path)).with_duration(duration)

    def zoom_effect(get_frame, t):
        scale = 1.0 + 0.05 * (t / duration)
        frame = get_frame(t)

        h, w = frame.shape[:2]
        new_w, new_h = int(w * scale), int(h * scale)

        try:
            import cv2
            resized = cv2.resize(frame, (new_w, new_h))
        except ImportError:
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            resized = np.array(img)

        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2

        return resized[start_y:start_y+h, start_x:start_x+w]

    return clip.with_make_frame(zoom_effect)


# =========================================================
# VIDEO GENERATION
# =========================================================

def merge_audio_and_visuals(
    script: Dict,
    audio_infos: List[Dict],
    version: str = "v1",
    visuals_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> str:

    if not audio_infos:
        raise ValueError("No audio data provided")

    from moviepy.video.VideoClip import ImageClip, ColorClip
    from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.audio.AudioClip import concatenate_audioclips
    import numpy as np

    title = script.get("title", "story")
    title_slug = slugify(title)

    if output_path is None:
        output_path = VIDEO_ROOT / version / f"{title_slug}.mp4"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        logging.info("Video already exists. Skipping render.")
        return str(output_path)

    clips = []
    audio_clips = []

    # Sort scenes by scene_number
    audio_infos = sorted(audio_infos, key=lambda x: x.get("scene_number", 0))

    for info in audio_infos:

        duration = max(0.5, float(info.get("duration", 0.5)))
        scene_no = int(info.get("scene_number", 0))

        # ---------------- FIND IMAGE ----------------

        image_path = None
        search_paths = []

        if visuals_dir:
            search_paths.append(Path(visuals_dir))

        search_paths.extend([
            VISUALS_ROOT / version / title_slug,
            VISUALS_ROOT / title_slug,
            Path("data") / title_slug
        ])

        for sp in search_paths:
            if not sp.exists():
                continue
            for ext in (".png", ".jpg", ".jpeg"):
                candidate = sp / f"scene_{scene_no:02d}{ext}"
                if candidate.exists():
                    image_path = candidate
                    break
            if image_path:
                break

        # ---------------- CREATE VIDEO CLIP ----------------

        if image_path:
            clip = animated_image_clip(image_path, duration)
        else:
            clip = ColorClip((1280, 720), color=(0, 0, 0)).with_duration(duration)

        clips.append(clip)

        # ---------------- AUDIO ----------------

        audio_file = info.get("file")
        if audio_file and Path(audio_file).exists():
            audio_clips.append(AudioFileClip(audio_file))

    if not audio_clips:
        raise ValueError("No valid audio clips found")

    # ---------------- MERGE ----------------

    video = concatenate_videoclips(clips, method="compose")
    audio = concatenate_audioclips(audio_clips)
    video = video.with_audio(audio)

    video.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )

    # Cleanup
    video.close()
    for c in clips:
        c.close()
    for a in audio_clips:
        a.close()

    logging.info(f"Video created: {output_path}")
    return str(output_path)


# =========================================================
# TTS GENERATION
# =========================================================

def generate_tts_for_script(script: Dict, version: str = "v1") -> List[Dict]:

    scenes = script.get("scenes", [])
    title = script.get("title", "story")
    title_slug = slugify(title)

    audio_dir = AUDIO_ROOT / version / title_slug
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_infos = []

    # Sort scenes
    scenes = sorted(scenes, key=lambda x: x.get("scene_number", 0))

    for scene in scenes:

        scene_no = int(scene.get("scene_number", 0))
        text = scene.get("text", "").strip()

        if not text:
            continue

        filename = audio_dir / f"scene_{scene_no:02d}.mp3"

        try:
            # 🔥 USE YOUR PRODUCTION TTS ENGINE
            generate_tts(
                narration=text,
                output_path=filename,
                lang="en",
                slow=False
            )

        except Exception as e:
            logging.error(f"TTS failed for scene {scene_no}: {e}")
            continue

        duration = get_audio_duration(filename)

        audio_infos.append({
            "scene_number": scene_no,
            "file": str(filename),
            "duration": duration
        })

    return audio_infos
