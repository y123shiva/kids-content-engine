"""
Export presets and thumbnail generation for videos.
Updated with Aspect Ratio handling, Font fallbacks, and Watermarking.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import json
from PIL import Image, ImageDraw, ImageFont

# MoviePy 2.x imports
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.video.fx as fx

class ExportPreset:
    """Video export preset with format-specific settings."""
    def __init__(
        self,
        name: str,
        resolution: Tuple[int, int],
        fps: int = 30,
        codec: str = "libx264",
        bitrate: str = "5000k",
        description: str = "",
    ):
        self.name = name
        self.resolution = resolution
        self.fps = fps
        self.codec = codec
        self.bitrate = bitrate
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "resolution": self.resolution,
            "fps": self.fps,
            "codec": self.codec,
            "bitrate": self.bitrate,
            "description": self.description,
        }

# Predefined export presets
PRESETS = {
    "youtube_1080p": ExportPreset("YouTube 1080p", (1920, 1080), 30, bitrate="8000k"),
    "youtube_720p": ExportPreset("YouTube 720p", (1280, 720), 24, bitrate="5000k"),
    "shorts_vertical": ExportPreset("YouTube Shorts", (1080, 1920), 30, bitrate="6000k"),
    "instagram_reels": ExportPreset("Instagram Reels", (1080, 1920), 30, bitrate="6000k"),
    "web_preview": ExportPreset("Web Preview", (640, 360), 24, bitrate="2000k"),
}

def get_preset(preset_name: str) -> Optional[ExportPreset]:
    return PRESETS.get(preset_name)

def list_presets() -> Dict[str, Dict]:
    return {name: preset.to_dict() for name, preset in PRESETS.items()}

def export_with_preset(
    input_video: Path,
    output_path: Path,
    preset_name: str = "youtube_720p",
    verbose: bool = True,
    add_watermark: bool = True
) -> str:
    """Export video with smart cropping for vertical formats."""
    preset = get_preset(preset_name)
    if not preset:
        raise ValueError(f"Unknown preset: {preset_name}")

    try:
        video = VideoFileClip(str(input_video))
        target_w, target_h = preset.resolution
        
        # --- ASPECT RATIO LOGIC ---
        # If the target is vertical (Shorts/Reels) and input is landscape
        if target_h > target_w and video.w > video.h:
            if verbose: print(f"  Transforming to Vertical: Cropping {preset_name}...")
            # 1. Scale so height matches
            video = video.resized(height=target_h)
            # 2. Crop the sides to center the action
            video = video.cropped(x_center=video.w/2, width=target_w)
        else:
            # Standard resize for same-aspect ratios
            video = video.resized(preset.resolution)

        # --- OPTIONAL WATERMARK ---
        if add_watermark:
            # Simple text watermark in the bottom right
            watermark = (TextClip(text="Bibo Kids TV", font_size=24, color='white', opacity=0.5)
                        .with_duration(video.duration)
                        .with_position(("right", "bottom")))
            video = CompositeVideoClip([video, watermark])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        video.write_videofile(
            str(output_path),
            fps=preset.fps,
            codec=preset.codec,
            audio_codec="aac",
            bitrate=preset.bitrate,
            logger="bar" if verbose else None
        )
        video.close()
        return str(output_path)
    except Exception as e:
        print(f"Error exporting {preset_name}: {e}")
        raise

def generate_thumbnail(
    video_path: Path,
    output_path: Optional[Path] = None,
    title: str = "",
    time_offset: float = 2.0,
    resolution: Tuple[int, int] = (1280, 720),
) -> str:
    """Generate high-quality thumbnail with font fallback."""
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_thumb.jpg"

    try:
        video = VideoFileClip(str(video_path))
        frame = video.get_frame(min(time_offset, video.duration - 0.1))
        img = Image.fromarray(frame).resize(resolution, Image.Resampling.LANCZOS)

        if title:
            draw = ImageDraw.Draw(img)
            # Safe Font Loading for Codespaces
            try:
                # Try common Linux/Codespace font paths
                font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "assets/fonts/rounded.ttf"]
                font = None
                for p in font_paths:
                    if Path(p).exists():
                        font = ImageFont.truetype(p, 60)
                        break
                if not font: font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()

            # Add a dark gradient/shadow for text readability
            shadow = Image.new("RGBA", img.size, (0, 0, 0, 100))
            img.paste(shadow, (0, 0), shadow)
            
            # Draw Centered Title
            w, h = draw.textbbox((0, 0), title, font=font)[2:]
            draw.text(((resolution[0]-w)/2, (resolution[1]-h)/2), title, fill="white", font=font)

        img.convert("RGB").save(output_path, "JPEG", quality=90)
        video.close()
        return str(output_path)
    except Exception as e:
        print(f"Thumbnail error: {e}")
        return ""

def create_video_metadata(title: str, description: str, tags: list = None) -> Dict:
    return {
        "title": title,
        "description": description,
        "tags": tags or ["kids", "education"],
        "category": "Education",
        "made_for_kids": True
    }

def save_metadata(metadata: Dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)