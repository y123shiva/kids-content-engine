import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def frames_to_video(
    frames_dir: Path, 
    audio_path: Path, 
    output_path: Path, 
    fps: int = 24
):
    """
    Stitches PNG frames into a video and attaches the narration audio.
    Uses FFmpeg for high-performance rendering.
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ffmpeg command breakdown:
    # -framerate: set input speed
    # -i: input pattern (looks for scene_X_0001.png, etc.)
    # -i: input audio
    # -c:v libx264: high quality video codec
    # -pix_fmt yuv420p: ensures compatibility with all players/browsers
    # -shortest: finish when the shortest input (usually audio) ends
    
    cmd = [
        'ffmpeg', '-y',                  # Overwrite if exists
        '-framerate', str(fps),          # Set frame rate
        '-i', f"{frames_dir}/scene_%d_%04d.png", # Match your filename pattern
        '-i', str(audio_path),           # The generated narration
        '-c:v', 'libx264',               # Video Codec
        '-preset', 'fast',               # Encoding speed
        '-pix_fmt', 'yuv420p',           # Standard color format
        '-c:a', 'aac',                   # Audio Codec
        '-b:a', '192k',                  # Audio Bitrate
        '-shortest',                     # Stop when audio ends
        str(output_path)
    ]

    try:
        logger.info(f"🚀 FFmpeg starting: {output_path.name}")
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"✅ Video rendered: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg Error: {e.stderr.decode()}")
        return False